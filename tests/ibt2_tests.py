#!/usr/bin/env python
"""I'll Be There, 2 (ibt2) - tests

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

import unittest
import requests
import monco

BASE_URL = 'http://localhost:3000/v1.0/'
DB_NAME = 'ibt2_test'

def dictInDict(d, dContainer):
    for k, v in d.viewitems():
        if k not in dContainer:
            return False
        if v != dContainer[k]:
            return False
    return True


class Ibt2Tests(unittest.TestCase):
    def setUp(self):
        self.monco_conn = monco.Monco(dbName=DB_NAME)
        self.connection = self.monco_conn.connection
        self.db = self.monco_conn.db
        self.db['attendees'].drop()
        self.db['days'].drop()
        self.db['groups'].drop()
        self.db['users'].remove({'username': 'newuser'})
        self.db['users'].remove({'username': 'newuser2'})

    def tearDown(self):
        self.db['attendees'].drop()
        self.db['days'].drop()
        self.db['groups'].drop()
        self.db['users'].remove({'username': 'newuser'})
        self.db['users'].remove({'username': 'newuser2'})

    def add_attendee(self, attendee):
        r = requests.post('%sattendees' % BASE_URL, json=attendee)
        r.raise_for_status()
        return r

    def test_add_attendee(self):
        attendee = {'name': 'A Name', 'day': '2017-01-15', 'group': 'A group'}
        r = self.add_attendee(attendee)
        rj = r.json()
        id_ = rj.get('_id')
        self.assertTrue(dictInDict(attendee, rj))
        r = requests.get(BASE_URL + 'attendees/' + id_)
        r.raise_for_status()
        rj = r.json()
        self.assertTrue(dictInDict(attendee, rj))

    def test_put_attendee(self):
        attendee = {'name': 'A Name', 'day': '2017-01-15', 'group': 'A group'}
        r = self.add_attendee(attendee)
        update = {'notes': 'A note'}
        r = requests.post(BASE_URL + 'attendees', json=attendee)
        r.raise_for_status()
        id_ = r.json().get('_id')
        r = requests.put(BASE_URL + 'attendees/' + id_, json=update)
        r.raise_for_status()
        r = requests.get('%s%s/%s' % (BASE_URL, 'attendees', id_))
        r.raise_for_status()
        rj = r.json()
        final = attendee.copy()
        final.update(update)
        self.assertTrue(dictInDict(final, rj))

    def test_delete_attendee(self):
        attendee = {'name': 'A Name', 'day': '2017-01-15', 'group': 'A group'}
        r = self.add_attendee(attendee)
        id_ = r.json().get('_id')
        r = requests.delete(BASE_URL + 'attendees/' + id_)
        r.raise_for_status()
        self.assertTrue(r.json().get('success'))

    def test_get_days(self):
        self.add_attendee({'day': '2017-01-15', 'name': 'A name', 'group': 'group A'})
        self.add_attendee({'day': '2017-01-16', 'name': 'A new name', 'group': 'group C'})
        self.add_attendee({'day': '2017-01-15', 'name': 'Another name', 'group': 'group A'})
        self.add_attendee({'day': '2017-01-15', 'name': 'Yet another name', 'group': 'group B'})
        r = requests.get(BASE_URL + 'days')
        r.raise_for_status()
        rj = r.json()
        self.assertEqual([x.get('day') for x in rj['days']], ['2017-01-15', '2017-01-16'])
        self.assertEqual([x.get('group') for x in rj['days'][0]['groups']], ['group A', 'group B'])
        self.assertTrue(len(rj['days'][0]['groups'][0]['attendees']) == 2)
        self.assertTrue(len(rj['days'][0]['groups'][1]['attendees']) == 1)
        self.assertEqual([x.get('group') for x in rj['days'][1]['groups']], ['group C'])
        self.assertTrue(len(rj['days'][1]['groups'][0]['attendees']) == 1)

    def test_get_days_summary(self):
        self.add_attendee({'day': '2017-01-15', 'name': 'A name', 'group': 'group A'})
        self.add_attendee({'day': '2017-01-16', 'name': 'A new name', 'group': 'group C'})
        self.add_attendee({'day': '2017-01-15', 'name': 'Another name', 'group': 'group A'})
        self.add_attendee({'day': '2017-01-15', 'name': 'Yet another name', 'group': 'group B'})
        r = requests.get(BASE_URL + 'days?summary=1')
        r.raise_for_status()
        rj = r.json()
        self.assertEqual(rj,
                         {"days": [{"groups_count": 2, "day": "2017-01-15"}, {"groups_count": 1, "day": "2017-01-16"}]})

    def test_create_user(self):
        r = requests.post(BASE_URL + 'users', json={'username': 'newuser', 'password': 'ibt2'})
        r.raise_for_status()
        s = self.login('newuser', 'ibt2')
        r = s.get(BASE_URL + 'users/current')
        r.raise_for_status()

    def test_update_user(self):
        r = requests.post(BASE_URL + 'users', json={'username': 'newuser', 'password': 'ibt2'})
        r.raise_for_status()
        id_ = r.json()['_id']
        r = requests.post(BASE_URL + 'users', json={'username': 'newuser2', 'password': 'ibt2'})
        r.raise_for_status()
        id2_ = r.json()['_id']
        r = requests.put(BASE_URL + 'users/' + id_, json={'email': 't@example.com'})
        self.assertRaises(r.raise_for_status)
        s = self.login('newuser', 'ibt2')
        r = s.put(BASE_URL + 'users/' + id_, json={'email': 'test@example.com'})
        r.raise_for_status()
        self.assertEqual(r.json().get('email'), 'test@example.com')
        r = s.put(BASE_URL + 'users/' + id2_, json={'email': 'test@example.com'})
        self.assertRaises(r.raise_for_status)
        s = self.login('admin', 'ibt2')
        r = s.put(BASE_URL + 'users/' + id_, json={'email': 'test2@example.com'})
        r.raise_for_status()
        self.assertEqual(r.json().get('email'), 'test2@example.com')

    def test_delete_user(self):
        r = requests.post(BASE_URL + 'users', json={'username': 'newuser', 'password': 'ibt2'})
        r.raise_for_status()
        id_ = r.json()['_id']
        r = requests.post(BASE_URL + 'users', json={'username': 'newuser2', 'password': 'ibt2'})
        r.raise_for_status()
        id2_ = r.json()['_id']
        r = requests.delete(BASE_URL + 'users/' + id_)
        self.assertRaises(r.raise_for_status)
        s = self.login('newuser', 'ibt2')
        r = s.delete(BASE_URL + 'users/' + id_)
        r.raise_for_status()
        r = s.delete(BASE_URL + 'users/' + id2_)
        self.assertRaises(r.raise_for_status)
        s = self.login('admin', 'ibt2')
        r = s.delete(BASE_URL + 'users/' + id2_)
        r.raise_for_status()

    def test_duplicate_user(self):
        r = requests.post(BASE_URL + 'users', json={'username': 'newuser', 'password': 'ibt2'})
        r.raise_for_status()
        r = requests.post(BASE_URL + 'users', json={'username': 'newuser', 'password': 'ibt3'})
        self.assertRaises(r.raise_for_status)

    def login(self, username, password):
        s = requests.Session()
        r = s.post(BASE_URL + 'login', json={'username': username, 'password': password})
        r.raise_for_status()
        return s

    def test_created_by(self):
        s = self.login('admin', 'ibt2')
        r = s.get(BASE_URL + 'users/current')
        r.raise_for_status()
        user_id = r.json()['_id']
        attendee = {'day': '2017-01-15', 'name': 'A name', 'group': 'group A'}
        r = s.post('%sattendees' % BASE_URL, json=attendee)
        r.raise_for_status()
        rj = r.json()
        self.assertEqual(user_id, rj['created_by'])
        self.assertEqual(user_id, rj['updated_by'])

    def test_put_day(self):
        day = {'day': '2017-01-16', 'notes': 'A day note'}
        self.add_attendee({'day': '2017-01-16', 'name': 'A new name', 'group': 'group C'})
        r = requests.put(BASE_URL + 'days', json=day)
        r.raise_for_status()
        rj = r.json()
        self.assertTrue(dictInDict(day, rj))
        r = requests.get(BASE_URL + 'days/2017-01-16')
        r.raise_for_status()
        rj = r.json()
        self.assertTrue(dictInDict(day, rj))

    def test_put_group(self):
        self.add_attendee({'day': '2017-01-16', 'name': 'A new name', 'group': 'A group'})
        group = {'group': 'A group', 'day': '2017-01-16', 'notes': 'A group note'}
        r = requests.put(BASE_URL + 'groups', json=group)
        r.raise_for_status()
        rj = r.json()
        self.assertTrue(dictInDict(group, rj))
        r = requests.get(BASE_URL + 'days/2017-01-16')
        r.raise_for_status()
        rj = r.json()
        self.assertTrue(dictInDict(group, rj['groups'][0]))


if __name__ == '__main__':
    unittest.main(verbosity=2)
