#!/usr/bin/env python
"""I'll Be There 2 (ibt2) - tests

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
    #@classmethod
    #def setUpClass(cls):
    def setUp(self):
        self.monco_conn = monco.Monco(dbName=DB_NAME)
        self.connection = self.monco_conn.connection
        self.db = self.monco_conn.db
        self.connection.drop_database(DB_NAME)

    def tearDown(self):
        self.add_attendee({'day': '2017-01-15', 'name': 'A name', 'group': 'group A'})
        self.add_attendee({'day': '2017-01-16', 'name': 'A new name', 'group': 'group C'})
        self.add_attendee({'day': '2017-01-15', 'name': 'Another name', 'group': 'group A'})
        self.add_attendee({'day': '2017-01-15', 'name': 'Yet another name', 'group': 'group B'})

    def add_attendee(self, attendee):
        r = requests.post('%sattendees' % BASE_URL, json=attendee)
        r.raise_for_status()
        return r

    def test_add_attendee(self):
        # POST /attendees/ {name: 'A Name', day: '2017-01-15', group: 'A group'}
        # GET /attendees/:id
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
        # POST /attendees/ {name: 'A Name', day: '2017-01-15', group: 'A group'}
        # GET /attendees/:id
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
        # POST /attendees/ {name: 'A Name', day: '2017-01-15', group: 'A group'}
        # GET /attendees/:id
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

    def _test_post_day_group(self):
        # POST /days/ {day: '2017-01-04'}
        # GET /days/2017-01-04
        day = '2017-01-15'
        query = {'day': day, 'groups': [{'name': 'group1'}]}
        r = requests.post(BASE_URL + 'days', json=query)
        r.raise_for_status()
        rj = r.json()
        self.assertTrue(dictInDict(query, rj))
        r = requests.get('%s%s/%s' % (BASE_URL, 'days', day))
        r.raise_for_status()
        rj = r.json()
        self.assertTrue(dictInDict(query, rj))

if __name__ == '__main__':
    unittest.main(verbosity=2)
