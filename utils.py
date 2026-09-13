# -*- coding: utf-8 -*-
"""ibt2 utils

Miscellaneous utilities.

Copyright 2016 Davide Alberani <da@mimante.net>
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
import hashlib
import datetime
import hmac
import secrets
from bson.objectid import ObjectId


def hash_password(password, salt=None):
    """Hash a password.

    :param password: the cleartext password
    :type password: str
    :param salt: optional legacy salt used when verifying old hashes
    :type salt: str

    :returns: the hashed password
    :rtype: str"""
    if salt is not None:
        pass_and_salt = ('%s%s' % (salt, password)).encode('utf-8', 'ignore')
        return '$%s$%s' % (salt, hashlib.sha512(pass_and_salt).hexdigest())
    salt = secrets.token_bytes(16)
    iterations = 600000
    digest = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt, iterations)
    return 'pbkdf2_sha256$%d$%s$%s' % (
        iterations, salt.hex(), digest.hex())


def verify_password(password, encoded):
    """Verify current PBKDF2 hashes and the original ibt2 hashes."""
    if not encoded:
        return False
    if encoded.startswith('pbkdf2_sha256$'):
        try:
            _, iterations, salt, expected = encoded.split('$', 3)
            actual = hashlib.pbkdf2_hmac(
                'sha256', password.encode('utf-8'), bytes.fromhex(salt),
                int(iterations))
            return hmac.compare_digest(actual.hex(), expected)
        except (TypeError, ValueError):
            return False
    if encoded.startswith('$'):
        try:
            salt, expected = encoded[1:].split('$', 1)
            actual = hashlib.sha512(
                ('%s%s' % (salt, password)).encode('utf-8')).hexdigest()
            return hmac.compare_digest(actual, expected)
        except ValueError:
            return False
    return False


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
