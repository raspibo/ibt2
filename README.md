# ibt2 - I'll be there, 2

**I'll be there, 2** is an oversimplified application to register attendees at a conference or event.

Basic workflow:
- if you want (not mandatory), login with your user; to create a new user, simply choose a username and a password. Benefit of logging in: only you or admins can edit/delete your entries.
- pick a date
- choose the name of a new group
- write your name
- rinse and repeat

It's recommended to login with username '''admin''' and password '''ibt2''', go to your personal page and change the password, if you've just installed ibt2.

## Install, run, develop and debug

To install it:
``` bash
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
sudo pip install tornado
sudo pip install pymongo
sudo pip install python-dateutil
git clone https://github.com/raspibo/ibt2
cd ibt2
```

Installation of [Node.js](https://nodejs.org/en/download/) and npm is left as an exercise to the reader.

To run it:
``` bash
# install dependencies (one time only)
npm install

# build for production with minification (each time the sources changes)
npm run build

# run the Python webserver at localhost:3000
npm run server
```

Now you can **point your browser to http://localhost:3000/** (that's the server for production)

If you want, you can **share a link to a specific day**, specifying it in the *yyyy-mm-dd* format, like: http://localhost:3000/#/day/2017-01-20

You can also **run the server in https**, putting in the *ssl* directory two files named *ibt2_key.pem* and *ibt2_cert.pem*

To run a development environment:
``` bash
# install dependencies (one time only)
npm install

# run the Python web server using a testing database
npm run devserver &

# serve with hot reload at localhost:8080
npm run dev

# only when the devserver is running, you can also run the testsuite
python ./tests/ibt2_tests.py
```

Your browser will automatically open http://localhost:8080/ (that's the server for development)


Development
===========

See the *docs/DEVELOPMENT.md* file for more information about how to contribute.


Technological stack
===================

- [VueJS](https://vuejs.org/) for the webApp
- [Vue Material](https://vuematerial.github.io/) for the UI components
- [vue Datepicker](https://github.com/charliekassel/vuejs-datepicker) for the datepicker
- [Tornado web](http://www.tornadoweb.org/) as web server
- [MongoDB](https://www.mongodb.org/) to store the data

The web part is incuded; you need to install Node.js, Tornado, MongoDB and the pymongo module on your system (no configuration needed).


License and copyright
=====================

Copyright 2016-2017 Davide Alberani <da@erlug.linux.it>, RaspiBO <info@raspibo.org>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

