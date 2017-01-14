#!/usr/bin/env python
"""I'll Be There, 2 (ibt2) - an oversimplified attendees registration system.

Copyright 2016-2017 Davide Alberani <da@erlug.linux.it>
                    RaspiBO <info@raspibo.org>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import re
import string
import logging
import datetime
from operator import itemgetter
import itertools

import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import define, options
import tornado.web
from tornado import gen, escape

import utils
import monco

API_VERSION = '1.0'


class BaseException(Exception):
    """Base class for ibt2 custom exceptions.

    :param message: text message
    :type message: str
    :param status: numeric http status code
    :type status: int"""
    def __init__(self, message, status=400):
        super(BaseException, self).__init__(message)
        self.message = message
        self.status = status


class InputException(BaseException):
    """Exception raised by errors in input handling."""
    pass


class BaseHandler(tornado.web.RequestHandler):
    """Base class for request handlers."""
    # Cache currently connected users.
    _users_cache = {}

    # A property to access the first value of each argument.
    arguments = property(lambda self: dict([(k, v[0])
        for k, v in self.request.arguments.iteritems()]))

    _bool_convert = {
        '0': False,
        'n': False,
        'f': False,
        'no': False,
        'off': False,
        'false': False,
        '1': True,
        'y': True,
        't': True,
        'on': True,
        'yes': True,
        'true': True
    }

    _re_split_salt = re.compile(r'\$(?P<salt>.+)\$(?P<hash>.+)')

    def write_error(self, status_code, **kwargs):
        """Default error handler."""
        if isinstance(kwargs.get('exc_info', (None, None))[1], BaseException):
            exc = kwargs['exc_info'][1]
            status_code = exc.status
            message = exc.message
        else:
            message = 'internal error'
        self.build_error(message, status=status_code)

    def is_api(self):
        """Return True if the path is from an API call."""
        return self.request.path.startswith('/v%s' % API_VERSION)

    def tobool(self, obj):
        """Convert some textual values to boolean."""
        if isinstance(obj, (list, tuple)):
            obj = obj[0]
        if isinstance(obj, (str, unicode)):
            obj = obj.lower()
        return self._bool_convert.get(obj, obj)

    def arguments_tobool(self):
        """Return a dictionary of arguments, converted to booleans where possible."""
        return dict([(k, self.tobool(v)) for k, v in self.arguments.iteritems()])

    def initialize(self, **kwargs):
        """Add every passed (key, value) as attributes of the instance."""
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    @property
    def current_user(self):
        """Retrieve current user name from the secure cookie."""
        return self.get_secure_cookie("user")

    @property
    def current_user_info(self):
        """Information about the current user."""
        current_user = self.current_user
        if current_user in self._users_cache:
            return self._users_cache[current_user]
        user_info = {}
        if current_user:
            user_info['username'] = current_user
            res = self.db.query('users', {'username': current_user})
            if res:
                user = res[0]
                user_info = user
        self._users_cache[current_user] = user_info
        return user_info

    def user_authorized(self, username, password):
        """Check if a combination of username/password is valid.

        :param username: username or email
        :type username: str
        :param password: password
        :type password: str

        :returns: tuple like (bool_user_is_authorized, dict_user_info)
        :rtype: dict"""
        query = [{'username': username}, {'email': username}]
        res = self.db.query('users', query)
        if not res:
            return (False, {})
        user = res[0]
        db_password = user.get('password') or ''
        if not db_password:
            return (False, {})
        match = self._re_split_salt.match(db_password)
        if not match:
            return (False, {})
        salt = match.group('salt')
        if utils.hash_password(password, salt=salt) == db_password:
            return (True, user)
        return (False, {})

    def build_error(self, message='', status=400):
        """Build and write an error message.

        :param message: textual message
        :type message: str
        :param status: HTTP status code
        :type status: int
        """
        self.set_status(status)
        self.write({'error': True, 'message': message})

    def logout(self):
        """Remove the secure cookie used fro authentication."""
        if self.current_user in self._users_cache:
            del self._users_cache[self.current_user]
        self.clear_cookie("user")


class RootHandler(BaseHandler):
    """Handler for the / path."""
    app_path = os.path.join(os.path.dirname(__file__), "dist")

    @gen.coroutine
    def get(self, *args, **kwargs):
        # serve the ./app/index.html file
        with open(self.app_path + "/index.html", 'r') as fd:
            self.write(fd.read())


class CollectionHandler(BaseHandler):
    """Base class for handlers that need to interact with the database backend.

    Introduce basic CRUD operations."""
    # set of documents we're managing (a collection in MongoDB or a table in a SQL database)
    document = None
    collection = None

    # set of documents used to store incremental sequences
    counters_collection = 'counters'

    _id_chars = string.ascii_lowercase + string.digits

    def _filter_results(self, results, params):
        """Filter a list using keys and values from a dictionary.

        :param results: the list to be filtered
        :type results: list
        :param params: a dictionary of items that must all be present in an original list item to be included in the return
        :type params: dict

        :returns: list of items that have all the keys with the same values as params
        :rtype: list"""
        if not params:
            return results
        params = monco.convert(params)
        filtered = []
        for result in results:
            add = True
            for key, value in params.iteritems():
                if key not in result or result[key] != value:
                    add = False
                    break
            if add:
                filtered.append(result)
        return filtered

    def _clean_dict(self, data):
        """Filter a dictionary (in place) to remove unwanted keywords in db queries.

        :param data: dictionary to clean
        :type data: dict"""
        if isinstance(data, dict):
            for key in data.keys():
                if isinstance(key, (str, unicode)) and key.startswith('$'):
                    del data[key]
        return data

    def apply_filter(self, data, filter_name):
        """Apply a filter to the data.

        :param data: the data to filter
        :returns: the modified (possibly also in place) data
        """
        filter_method = getattr(self, 'filter_%s' % filter_name, None)
        if filter_method is not None:
            data = filter_method(data)
        return data


class AttendeesHandler(CollectionHandler):
    document = 'attendee'
    collection = 'attendees'

    @gen.coroutine
    def get(self, id_=None, **kwargs):
        if id_:
            output = self.db.getOne(self.collection, {'_id': id_})
        else:
            output = {self.collection: self.db.query(self.collection, self.arguments)}
        self.write(output)

    @gen.coroutine
    def post(self, **kwargs):
        data = escape.json_decode(self.request.body or '{}')
        self._clean_dict(data)
        user_info = self.current_user_info
        user_id = user_info.get('_id')
        now = datetime.datetime.now()
        data['created_by'] = user_id
        data['created_at'] = now
        data['updated_by'] = user_id
        data['updated_at'] = now
        doc = self.db.add(self.collection, data)
        doc = self.apply_filter(doc, 'create')
        self.write(doc)

    @gen.coroutine
    def put(self, id_, **kwargs):
        data = escape.json_decode(self.request.body or '{}')
        self._clean_dict(data)
        if '_id' in data:
            del data['_id']
        user_info = self.current_user_info
        user_id = user_info.get('_id')
        now = datetime.datetime.now()
        data['updated_by'] = user_id
        data['updated_at'] = now
        merged, doc = self.db.update(self.collection, {'_id': id_}, data)
        doc = self.apply_filter(doc, 'update')
        self.write(doc)

    @gen.coroutine
    def delete(self, id_=None, **kwargs):
        if id_ is not None:
            howMany = self.db.delete(self.collection, id_)
            self.write({'success': True, 'deleted entries': howMany.get('n')})
        else:
            self.write({'success': False})


class DaysHandler(CollectionHandler):
    """Handle requests for Days."""

    def _summarize(self, days):
        res = []
        for day in days:
            res.append({'day': day['day'], 'groups_count': len(day.get('groups', []))})
        return res

    @gen.coroutine
    def get(self, day=None, **kwargs):
        params = self.arguments
        summary = params.get('summary', False)
        if summary:
            del params['summary']
        start = params.get('start')
        if start:
            del params['start']
        end = params.get('end')
        if end:
            del params['end']
        if day:
            params['day'] = day
        else:
            if start:
                params['day'] = {'$gte': start}
            if end:
                if 'day' not in params:
                    params['day'] = {}
                if end.count('-') == 0:
                    end += '-13'
                elif end.count('-') == 1:
                    end += '-31'
                params['day'].update({'$lte': end})
        results = self.db.query('attendees', params)
        days = []
        dayData = {}
        try:
            sortedDays = []
            for result in results:
                if not ('day' in result and 'group' in result and 'name' in result):
                    self.logger.warn('unable to parse entry; dayData: %s', dayData)
                    continue
                sortedDays.append(result)
            sortedDays = sorted(sortedDays, key=itemgetter('day'))
            for d, dayItems in itertools.groupby(sortedDays, key=itemgetter('day')):
                dayData = {'day': d, 'groups': []}
                for group, attendees in itertools.groupby(sorted(dayItems, key=itemgetter('group')),
                                                          key=itemgetter('group')):
                    attendees = sorted(attendees, key=itemgetter('_id'))
                    dayData['groups'].append({'group': group, 'attendees': attendees})
                days.append(dayData)
        except Exception as e:
            self.logger.warn('unable to parse entry; dayData: %s', dayData)
        if summary:
            days = self._summarize(days)
        if not day:
            self.write({'days': days})
        elif days:
            self.write(days[0])
        else:
            self.write({})


class UsersHandler(CollectionHandler):
    """Handle requests for Users."""
    document = 'user'
    collection = 'users'

    def filter_get(self, data):
        if 'password' in data:
            del data['password']
        return data

    def filter_get_all(self, data):
        if 'users' not in data:
            return data
        for user in data['users']:
            if 'password' in user:
                del user['password']
        return data

    @gen.coroutine
    def get(self, id_=None, resource=None, resource_id=None, acl=True, **kwargs):
        super(UsersHandler, self).get(id_, resource, resource_id, acl=acl, **kwargs)

    def filter_input_post_all(self, data):
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()
        email = (data.get('email') or '').strip()
        if not (username and password):
            raise InputException('missing username or password')
        res = self.db.query('users', {'username': username})
        if res:
            raise InputException('username already exists')
        return {'username': username, 'password': utils.hash_password(password),
                'email': email}

    def filter_input_put(self, data):
        old_pwd = data.get('old_password')
        new_pwd = data.get('new_password')
        if old_pwd is not None:
            del data['old_password']
        if new_pwd is not None:
            del data['new_password']
            authorized, user = self.user_authorized(data['username'], old_pwd)
            if not (authorized and self.current_user == data['username']):
                raise InputException('not authorized to change password')
            data['password'] = utils.hash_password(new_pwd)
        if '_id' in data:
            # Avoid overriding _id
            del data['_id']
        return data

    @gen.coroutine
    def put(self, id_=None, resource=None, resource_id=None, **kwargs):
        if id_ is None:
            return self.build_error(status=404, message='unable to access the resource')
        if str(self.current_user_info.get('_id')) != id_:
            return self.build_error(status=401, message='insufficient permissions: current user')
        super(UsersHandler, self).put(id_, resource, resource_id, **kwargs)


class SettingsHandler(BaseHandler):
    """Handle requests for Settings."""
    @gen.coroutine
    def get(self, **kwargs):
        query = self.arguments_tobool()
        settings = self.db.query('settings', query)
        self.write({'settings': settings})


class CurrentUserHandler(BaseHandler):
    """Handle requests for information about the logged in user."""
    @gen.coroutine
    def get(self, **kwargs):
        user_info = self.current_user_info or {}
        if 'password' in user_info:
            del user_info['password']
        self.write(user_info)


class LoginHandler(RootHandler):
    """Handle user authentication requests."""

    @gen.coroutine
    def get(self, **kwargs):
        # show the login page
        if self.is_api():
            self.set_status(401)
            self.write({'error': True,
                'message': 'authentication required'})

    @gen.coroutine
    def post(self, *args, **kwargs):
        # authenticate a user
        try:
            password = self.get_body_argument('password')
            username = self.get_body_argument('username')
        except tornado.web.MissingArgumentError:
            data = escape.json_decode(self.request.body or '{}')
            username = data.get('username')
            password = data.get('password')
        if not (username and password):
            self.set_status(401)
            self.write({'error': True, 'message': 'missing username or password'})
            return
        authorized, user = self.user_authorized(username, password)
        if authorized and user.get('username'):
            username = user['username']
            logging.info('successful login for user %s' % username)
            self.set_secure_cookie("user", username)
            user_info = self.current_user_info
            if 'password' in user_info:
                del user_info['password']
            self.write(user_info)
            return
        logging.info('login failed for user %s' % username)
        self.set_status(401)
        self.write({'error': True, 'message': 'wrong username and password'})


class LogoutHandler(BaseHandler):
    """Handle user logout requests."""
    @gen.coroutine
    def get(self, **kwargs):
        # log the user out
        logging.info('logout')
        self.logout()
        self.write({'error': False, 'message': 'logged out'})


def run():
    """Run the Tornado web application."""
    # command line arguments; can also be written in a configuration file,
    # specified with the --config argument.
    define("port", default=3000, help="run on the given port", type=int)
    define("address", default='', help="bind the server at the given address", type=str)
    define("data_dir", default=os.path.join(os.path.dirname(__file__), "data"),
            help="specify the directory used to store the data")
    define("ssl_cert", default=os.path.join(os.path.dirname(__file__), 'ssl', 'ibt2_cert.pem'),
            help="specify the SSL certificate to use for secure connections")
    define("ssl_key", default=os.path.join(os.path.dirname(__file__), 'ssl', 'ibt2_key.pem'),
            help="specify the SSL private key to use for secure connections")
    define("mongo_url", default=None,
            help="URL to MongoDB server", type=str)
    define("db_name", default='ibt2',
            help="Name of the MongoDB database to use", type=str)
    define("authentication", default=False, help="if set to true, authentication is required")
    define("debug", default=False, help="run in debug mode")
    define("config", help="read configuration file",
            callback=lambda path: tornado.options.parse_config_file(path, final=False))
    tornado.options.parse_command_line()

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if options.debug:
        logger.setLevel(logging.DEBUG)

    ssl_options = {}
    if os.path.isfile(options.ssl_key) and os.path.isfile(options.ssl_cert):
        ssl_options = dict(certfile=options.ssl_cert, keyfile=options.ssl_key)

    # database backend connector
    db_connector = monco.Monco(url=options.mongo_url, dbName=options.db_name)
    init_params = dict(db=db_connector, data_dir=options.data_dir, listen_port=options.port,
            authentication=options.authentication, logger=logger, ssl_options=ssl_options)

    # If not present, we store a user 'admin' with password 'ibt2' into the database.
    if not db_connector.query('users', {'username': 'admin'}):
        db_connector.add('users',
                {'username': 'admin', 'password': utils.hash_password('ibt2'),
                 'isAdmin': True})

    # If present, use the cookie_secret stored into the database.
    cookie_secret = db_connector.query('settings', {'setting': 'server_cookie_secret'})
    if cookie_secret:
        cookie_secret = cookie_secret[0]['cookie_secret']
    else:
        # the salt guarantees its uniqueness
        cookie_secret = utils.hash_password('__COOKIE_SECRET__')
        db_connector.add('settings',
                {'setting': 'server_cookie_secret', 'cookie_secret': cookie_secret})

    _days_path = r"/days/?(?P<day>[\d_-]+)?"
    _attendees_path = r"/days/(?P<day_id>[\d_-]+)/groups/(?P<group_id>[\w\d_\ -]+)/attendees/?(?P<attendee_id>[\w\d_\ -]+)?"
    _current_user_path = r"/users/current/?"
    _users_path = r"/users/?(?P<id_>[\w\d_-]+)?/?(?P<resource>[\w\d_-]+)?/?(?P<resource_id>[\w\d_-]+)?"
    _attendees_path = r"/attendees/?(?P<id_>[\w\d_-]+)?"
    application = tornado.web.Application([
            (_attendees_path, AttendeesHandler, init_params),
            (r'/v%s%s' % (API_VERSION, _attendees_path), AttendeesHandler, init_params),
            (_days_path, DaysHandler, init_params),
            (r'/v%s%s' % (API_VERSION, _days_path), DaysHandler, init_params),
            (_current_user_path, CurrentUserHandler, init_params),
            (r'/v%s%s' % (API_VERSION, _current_user_path), CurrentUserHandler, init_params),
            (_users_path, UsersHandler, init_params),
            (r'/v%s%s' % (API_VERSION, _users_path), UsersHandler, init_params),
            (r"/(?:index.html)?", RootHandler, init_params),
            (r"/settings", SettingsHandler, init_params),
            (r'/login', LoginHandler, init_params),
            (r'/v%s/login' % API_VERSION, LoginHandler, init_params),
            (r'/logout', LogoutHandler),
            (r'/v%s/logout' % API_VERSION, LogoutHandler),
            (r'/?(.*)', tornado.web.StaticFileHandler, {"path": "dist"})
        ],
        static_path=os.path.join(os.path.dirname(__file__), "dist/static"),
        cookie_secret='__COOKIE_SECRET__',
        login_url='/login',
        debug=options.debug)
    http_server = tornado.httpserver.HTTPServer(application, ssl_options=ssl_options or None)
    logger.info('Start serving on %s://%s:%d', 'https' if ssl_options else 'http',
                                                 options.address if options.address else '127.0.0.1',
                                                 options.port)
    http_server.listen(options.port, options.address)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        print('Stop server')
