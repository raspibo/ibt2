# -*- coding: utf-8 -*-
"""ibt2 utils

Miscellaneous utilities.

Copyright 2016 Davide Alberani <da@erlug.linux.it>
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

import json
import string
import random
import hashlib
import datetime
from bson.objectid import ObjectId


def hash_password(password, salt=None):
    """Hash a password.

    :param password: the cleartext password
    :type password: str
    :param salt: the optional salt (randomly generated, if None)
    :type salt: str

    :returns: the hashed password
    :rtype: str"""
    if salt is None:
        salt_pool = string.ascii_letters + string.digits
        salt = ''.join(random.choice(salt_pool) for x in range(32))
    pass_and_salt = '%s%s' % (salt, password)
    pass_and_salt = pass_and_salt.encode('utf-8', 'ignore')
    hash_ = hashlib.sha512(pass_and_salt)
    return '$%s$%s' % (salt, hash_.hexdigest())


class ImprovedEncoder(json.JSONEncoder):
    """Enhance the default JSON encoder to serialize datetime and ObjectId instances."""
    def default(self, o):
        if isinstance(o, bytes):
            try:
                return o.decode('utf-8')
            except:
                pass
        elif isinstance(o, (datetime.datetime, datetime.date,
                          datetime.time, datetime.timedelta, ObjectId)):
            try:
                return str(o)
            except:
                pass
        elif isinstance(o, set):
            return list(o)
        return json.JSONEncoder.default(self, o)


# Inject our class as the default encoder.
json._default_encoder = ImprovedEncoder()

