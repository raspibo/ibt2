#!/usr/bin/env python3
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

API_VERSION = '1.1'


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

    # set of documents we're managing (a collection in MongoDB or a table in a SQL database)
    document = None
    collection = None

    # A property to access the first value of each argument.
    arguments = property(lambda self: dict([(k, v[0].decode('utf-8'))
        for k, v in self.request.arguments.items()]))

    # Arguments suitable for a query on MongoDB.
    clean_arguments = property(lambda self: self._clean_dict(self.arguments))

    _re_split_salt = re.compile(r'\$(?P<salt>.+)\$(?P<hash>.+)')

    @property
    def clean_body(self):
        """Return a clean dictionary from a JSON body, suitable for a query on MongoDB.

        :returns: a clean copy of the body arguments
        :rtype: dict"""
        data = escape.json_decode(self.request.body or '{}')
        return self._clean_dict(data)

    def _clean_dict(self, data):
        """Filter a dictionary (in place) to remove unwanted keywords in db queries.

        :param data: dictionary to clean
        :type data: dict"""
        if isinstance(data, dict):
            for key in list(data.keys()):
                if (isinstance(key, str) and key.startswith('$')) or key in ('_id', 'created_by', 'created_at',
                                                                    'updated_by', 'updated_at', 'isRegistered'):
                    del data[key]
        return data

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

    def initialize(self, **kwargs):
        """Add every passed (key, value) as attributes of the instance."""
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def current_user(self):
        """Retrieve current user ID from the secure cookie."""
        current_user = self.get_secure_cookie("user")
        if isinstance(current_user, bytes):
            current_user = current_user.decode('utf-8')
        return current_user

    @property
    def current_user_info(self):
        """Information about the current user.

        :returns: full information about the current user
        :rtype: dict"""
        current_user = self.current_user
        if current_user in self._users_cache:
            return self._users_cache[current_user]
        user_info = {}
        if current_user:
            user_info['_id'] = current_user
            user = self.db.getOne('users', {'_id': user_info['_id']})
            if user:
                user_info = user
                user_info['isRegistered'] = True
        self._users_cache[current_user] = user_info
        return user_info

    def is_registered(self):
        """Check if the current user is registered.

        :returns: True if a registered user is logged in
        :rtype: bool"""
        return self.current_user_info.get('isRegistered')

    def is_admin(self):
        """Check if the current user is an admin.

        :returns: True if the logged in user is an admin
        :rtype: bool"""
        return self.current_user_info.get('isAdmin')

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

    def has_permission(self, owner_id):
        """Check if the given owner_id matches with the current user or the logged in user is an admin; if not,
        build an error reply.

        :param owner_id: owner ID to check against
        :type owner_id: str, ObjectId, None

        :returns: if the logged in user has the permission
        :rtype: bool"""
        if (owner_id and str(self.current_user) != str(owner_id) and not
                self.is_admin()):
            self.build_error(status=401, message='insufficient permissions: must be the owner or admin')
            return False
        return True

    def logout(self):
        """Remove the secure cookie used fro authentication."""
        if self.current_user in self._users_cache:
            del self._users_cache[self.current_user]
        self.clear_cookie("user")

    def add_access_info(self, doc):
        """Add created/updated by/at to a document (modified in place and returned).

        :param doc: the doc to be updated
        :type doc: dict
        :returns: the updated document
        :rtype: dict"""
        user_id = self.current_user
        now = datetime.datetime.utcnow()
        if 'created_by' not in doc:
            doc['created_by'] = user_id
        if 'created_at' not in doc:
            doc['created_at'] = now
        doc['updated_by'] = user_id
        doc['updated_at'] = now
        return doc

    @staticmethod
    def update_global_settings(db_connector, settings=None):
        """Update global settings from the db.

        :param db_connector: database connector
        :type db_connector: Monco instance
        :param settings: the dict to update (in place, and returned)
        :type settings: dict

        :returns: the updated dictionary, also modified in place
        :rtype: dict"""
        if settings is None:
            settings = {}
        settings.clear()
        for setting in db_connector.query('settings'):
            if not ('_id' in setting and 'value' in setting):
                continue
            settings[setting['_id']] = setting['value']
        return settings


class RootHandler(BaseHandler):
    """Handler for the / path."""
    app_path = os.path.join(os.path.dirname(__file__), "dist")

    @gen.coroutine
    def get(self, *args, **kwargs):
        # serve the ./app/index.html file
        with open(self.app_path + "/index.html", 'r') as fd:
            self.write(fd.read())


class AttendeesHandler(BaseHandler):
    document = 'attendee'
    collection = 'attendees'

    @gen.coroutine
    def get(self, id_=None, **kwargs):
        if id_:
            output = self.db.getOne(self.collection, {'_id': id_})
        else:
            output = {self.collection: self.db.query(self.collection, self.clean_arguments)}
        self.write(output)

    @gen.coroutine
    def post(self, **kwargs):
        data = self.clean_body
        for key in 'name', 'group', 'day':
            value = (data.get(key) or '').strip()
            if not value:
                return self.build_error(status=404, message="%s can't be empty" % key)
            data[key] = value
        self.add_access_info(data)
        doc = self.db.add(self.collection, data)
        self.write(doc)

    @gen.coroutine
    def put(self, id_, **kwargs):
        data = self.clean_body
        doc = self.db.getOne(self.collection, {'_id': id_}) or {}
        if not doc:
            return self.build_error(status=404, message='unable to access the resource')
        if not self.has_permission(doc.get('created_by')):
            return
        if self.global_settings.get('protectUnregistered') and not self.is_admin():
            return self.build_error(status=401, message='insufficient permissions: must be admin')
        self.add_access_info(data)
        merged, doc = self.db.update(self.collection, {'_id': id_}, data)
        self.write(doc)

    @gen.coroutine
    def delete(self, id_=None, **kwargs):
        if id_ is None:
            return self.build_error(status=404, message='unable to access the resource')
        doc = self.db.getOne(self.collection, {'_id': id_}) or {}
        if not doc:
            return self.build_error(status=404, message='unable to access the resource')
        if not self.has_permission(doc.get('created_by')):
            return
        if self.global_settings.get('protectUnregistered') and not self.is_admin():
            return self.build_error(status=401, message='insufficient permissions: must be admin')
        howMany = self.db.delete(self.collection, id_)
        self.write({'success': True, 'deleted entries': howMany.get('n')})


class DaysHandler(BaseHandler):
    """Handle requests for Days."""
    def _summarize(self, days):
        res = []
        for day in days:
            res.append({'day': day['day'], 'groups_count': len(day.get('groups', []))})
        return res

    @gen.coroutine
    def get(self, day=None, **kwargs):
        params = self.clean_arguments
        summary = params.get('summary', False)
        if summary:
            del params['summary']
        start = params.get('start')
        if start:
            del params['start']
        end = params.get('end')
        if end:
            del params['end']
        base = {}
        groupsDetails = {}
        if day:
            params['day'] = day
            base = self.db.getOne('days', {'day': day})
            groupsDetails = dict([(x['group'], x) for x in self.db.query('groups', {'day': day})])
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
                    groupData = groupsDetails.get(group) or {}
                    groupData.update({'group': group, 'attendees': attendees})
                    dayData['groups'].append(groupData)
                days.append(dayData)
        except Exception as e:
            self.logger.warn('unable to parse entry; dayData: %s error: %s', dayData, e)
        if summary:
            days = self._summarize(days)
        if not day:
            self.write({'days': days})
        elif days:
            base.update(days[0])
            self.write(base)
        else:
            self.write(base)


class DaysInfoHandler(BaseHandler):
    """Handle requests for Days info."""
    @gen.coroutine
    def put(self, day='', **kwargs):
        day = day.strip()
        if not day:
            return self.build_error(status=404, message='unable to access the resource')
        data = self.clean_body
        if 'notes' in data and self.global_settings.get('protectDayNotes') and not self.is_admin():
            return self.build_error(status=401, message='insufficient permissions: must be admin')
        data['day'] = day
        self.add_access_info(data)
        merged, doc = self.db.update('days', {'day': day}, data)
        self.write(doc)


class GroupsHandler(BaseHandler):
    """Handle requests for Groups."""
    @gen.coroutine
    def put(self, day='', group='', **kwargs):
        day = day.strip()
        group = group.strip()
        if not (day and group):
            return self.build_error(status=404, message='unable to access the resource')
        data = self.clean_body
        newName = (data.get('newName') or '').strip()
        if newName:
            if self.global_settings.get('protectGroupName') and not self.is_admin():
                return self.build_error(status=401, message='insufficient permissions: must be admin')
            query = {'day': day, 'group': group}
            data = {'group': newName}
            self.db.updateMany('attendees', query, data)
            self.db.updateMany('groups', query, data)
            self.write({'success': True})
        else:
            self.write({'success': False})

    @gen.coroutine
    def delete(self, day='', group='', **kwargs):
        day = day.strip()
        group = group.strip()
        if not (day and group):
            return self.build_error(status=404, message='unable to access the resource')
        if not self.is_admin():
            return self.build_error(status=401, message='insufficient permissions: must be admin')
        query = {'day': day, 'group': group}
        howMany = self.db.delete('attendees', query)
        self.db.delete('groups', query)
        self.write({'success': True, 'deleted entries': howMany.get('n')})


class GroupsInfoHandler(BaseHandler):
    """Handle requests for Groups Info."""
    @gen.coroutine
    def put(self, day='', group='', **kwargs):
        day = day.strip()
        group = group.strip()
        if not (day and group):
            return self.build_error(status=404, message='unable to access the resource')
        data = self.clean_body
        if 'notes' in data and self.global_settings.get('protectGroupNotes') and not self.is_admin():
            return self.build_error(status=401, message='insufficient permissions: must be admin')
        data['day'] = day
        data['group'] = group
        self.add_access_info(data)
        merged, doc = self.db.update('groups', {'day': day, 'group': group}, data)
        self.write(doc)


class UsersHandler(BaseHandler):
    """Handle requests for Users."""
    document = 'user'
    collection = 'users'

    @gen.coroutine
    def get(self, id_=None, **kwargs):
        if id_:
            if not self.has_permission(id_):
                return
            output = self.db.getOne(self.collection, {'_id': id_})
            if 'password' in output:
                del output['password']
        else:
            if not self.is_admin():
                return self.build_error(status=401, message='insufficient permissions: must be an admin')
            output = {self.collection: self.db.query(self.collection, self.clean_arguments)}
            for user in output['users']:
                if 'password' in user:
                    del user['password']
        self.write(output)

    @gen.coroutine
    def post(self, **kwargs):
        data = self.clean_body
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()
        email = (data.get('email') or '').strip()
        if not (username and password):
            raise InputException('missing username or password')
        res = self.db.query('users', {'username': username})
        if res:
            raise InputException('username already exists')
        data['username'] = username
        data['password'] = utils.hash_password(password)
        data['email'] = email
        self.add_access_info(data)
        if 'isAdmin' in data and not self.is_admin():
            del data['isAdmin']
        doc = self.db.add(self.collection, data)
        if 'password' in doc:
            del doc['password']
        self.write(doc)

    @gen.coroutine
    def put(self, id_=None, **kwargs):
        data = self.clean_body
        if id_ is None:
            return self.build_error(status=404, message='unable to access the resource')
        if not self.has_permission(id_):
            return
        if 'username' in data:
            del data['username']
        if 'isAdmin' in data and (str(self.current_user) == id_ or not self.is_admin()):
            del data['isAdmin']
        if 'password' in data:
            password = (data['password'] or '').strip()
            if password:
                data['password'] = utils.hash_password(password)
            else:
                del data['password']
        self.add_access_info(data)
        merged, doc = self.db.update(self.collection, {'_id': id_}, data)
        if 'password' in doc:
            del doc['password']
        self.write(doc)

    @gen.coroutine
    def delete(self, id_=None, **kwargs):
        if id_ is None:
            return self.build_error(status=404, message='unable to access the resource')
        if not self.has_permission(id_):
            return self.build_error(status=401, message='insufficient permissions: must be admin')
        if id_ == self.current_user:
            return self.build_error(status=401, message='unable to delete the current user; ask an admin')
        doc = self.db.getOne(self.collection, {'_id': id_})
        if not doc:
            return self.build_error(status=404, message='unable to access the resource')
        if doc.get('username') == 'admin':
            return self.build_error(status=401, message='unable to delete the admin user')
        howMany = self.db.delete(self.collection, id_)
        if id_ in self._users_cache:
            del self._users_cache[id_]
        self.write({'success': True, 'deleted entries': howMany.get('n')})


class CurrentUserHandler(BaseHandler):
    """Handle requests for information about the logged in user."""
    @gen.coroutine
    def get(self, **kwargs):
        user_info = self.current_user_info or {}
        if 'password' in user_info:
            del user_info['password']
        self.write(user_info)


class SettingsHandler(BaseHandler):
    """Handle global settings."""
    collection = 'settings'

    def get(self, id_=None):
        query = {}
        if id_ is not None:
            query['_id'] = id_
        res = self.db.query(self.collection, query)
        res = dict((i.get('_id'), i.get('value')) for i in res if '_id' in i and isinstance(i.get('_id'), str))
        if id_ is not None:
            res = {id_: res.get(id_)}
        self.write(res)

    def post(self, id_=None):
        if not self.is_admin():
            return self.build_error(status=401, message='insufficient permissions: must be an admin')
        data = self.clean_body
        if id_ is not None:
            # if we access a specific resource, we assume the data is in {_id: value} format
            if id_ not in data:
                return self.build_error(status=404, message='incomplete data')
                return
            data = {id_: data[id_]}
        for key, value in data.items():
            if self.db.get(self.collection, key):
                self.db.update(self.collection, {'_id': key}, {'value': value})
            else:
                self.db.add(self.collection, {'_id': key, 'value': value})
        settings = SettingsHandler.update_global_settings(self.db, self.global_settings)
        self.write(settings)

    put = post


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
            data = self.clean_body
            username = data.get('username')
            password = data.get('password')
        if not (username and password):
            self.set_status(401)
            self.write({'error': True, 'message': 'missing username or password'})
            return
        authorized, user = self.user_authorized(username, password)
        if authorized and 'username' in user and '_id' in user:
            id_ = str(user['_id'])
            username = user['username']
            logging.info('successful login for user %s (id: %s)' % (username, id_))
            self.set_secure_cookie("user", id_)
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
    define("ssl_cert", default=os.path.join(os.path.dirname(__file__), 'ssl', 'ibt2_cert.pem'),
            help="specify the SSL certificate to use for secure connections")
    define("ssl_key", default=os.path.join(os.path.dirname(__file__), 'ssl', 'ibt2_key.pem'),
            help="specify the SSL private key to use for secure connections")
    define("mongo_url", default=None,
            help="URL to MongoDB server", type=str)
    define("db_name", default='ibt2',
            help="Name of the MongoDB database to use", type=str)
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

    # global settings stored in the db
    global_settings = {}
    BaseHandler.update_global_settings(db_connector, global_settings)

    init_params = dict(db=db_connector, listen_port=options.port, logger=logger,
                       ssl_options=ssl_options, global_settings=global_settings)

    # If not present, we store a user 'admin' with password 'ibt2' into the database.
    if not db_connector.query('users', {'username': 'admin'}):
        db_connector.add('users',
                {'username': 'admin', 'password': utils.hash_password('ibt2'),
                 'isAdmin': True})

    # If present, use the cookie_secret stored into the database.
    cookie_secret = db_connector.get('server_settings', 'server_cookie_secret')
    if cookie_secret:
        cookie_secret = cookie_secret['value']
    else:
        # the salt guarantees its uniqueness
        cookie_secret = utils.hash_password('__COOKIE_SECRET__')
        db_connector.add('server_settings',
                {'_id': 'server_cookie_secret', 'value': cookie_secret})

    _days_path = r"/days/?(?P<day>[\d_-]+)?"
    _days_info_path = r"/days/(?P<day>[\d_-]+)/info"
    _groups_path = r"/days/(?P<day>[\d_-]+)/groups/(?P<group>.+?)"
    _groups_info_path = r"/days/(?P<day>[\d_-]+)/groups/(?P<group>.+?)/info"
    _attendees_path = r"/attendees/?(?P<id_>[\w\d_-]+)?"
    _current_user_path = r"/users/current/?"
    _users_path = r"/users/?(?P<id_>[\w\d_-]+)?/?(?P<resource>[\w\d_-]+)?/?(?P<resource_id>[\w\d_-]+)?"
    _settings_path = r"/settings/?(?P<id_>[\w\d_ -]+)?/?"
    application = tornado.web.Application([
            (_attendees_path, AttendeesHandler, init_params),
            (r'/v%s%s' % (API_VERSION, _attendees_path), AttendeesHandler, init_params),
            (_groups_info_path, GroupsInfoHandler, init_params),
            (r'/v%s%s' % (API_VERSION, _groups_info_path), GroupsInfoHandler, init_params),
            (_groups_path, GroupsHandler, init_params),
            (r'/v%s%s' % (API_VERSION, _groups_path), GroupsHandler, init_params),
            (_days_path, DaysHandler, init_params),
            (r'/v%s%s' % (API_VERSION, _days_path), DaysHandler, init_params),
            (_days_info_path, DaysInfoHandler, init_params),
            (r'/v%s%s' % (API_VERSION, _days_info_path), DaysInfoHandler, init_params),
            (_current_user_path, CurrentUserHandler, init_params),
            (r'/v%s%s' % (API_VERSION, _current_user_path), CurrentUserHandler, init_params),
            (_users_path, UsersHandler, init_params),
            (r'/v%s%s' % (API_VERSION, _users_path), UsersHandler, init_params),
            (_settings_path, SettingsHandler, init_params),
            (r'/v%s%s' % (API_VERSION, _settings_path), SettingsHandler, init_params),
            (r"/(?:index.html)?", RootHandler, init_params),
            (r'/login', LoginHandler, init_params),
            (r'/v%s/login' % API_VERSION, LoginHandler, init_params),
            (r'/logout', LogoutHandler),
            (r'/v%s/logout' % API_VERSION, LogoutHandler),
            (r'/?(.*)', tornado.web.StaticFileHandler, {"path": "dist"})
        ],
        static_path=os.path.join(os.path.dirname(__file__), "dist/static"),
        cookie_secret=cookie_secret,
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
