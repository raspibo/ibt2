# ibt2 - I'll be there, 2

**I'll be there, 2** is an oversimplified application to register attendees at a conference or event.

Basic workflow:
- if you want (not mandatory), login with your user; to create a new user, simply choose a username and a password. Benefit of logging in: only you or admins can edit/delete your entries.
- pick a date
- choose the group you want to join or the name of a new group
- write your name and, optionally, a note
- rinse and repeat

It's recommended to login with username **admin** and password **ibt2**, go to your personal page and change the password, if you've just installed ibt2. The *admin* user can grant super cow powers to any other user.

For the notes, you can use the [Markdown](https://daringfireball.net/projects/markdown/) syntax.

# Demo

See [https://ibt2.ismito.it:3002/](https://ibt2.ismito.it:3002/)

## Install, run, develop and debug

To install it:
``` bash
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
# if you want to install these modules for an unprivileged user, add --user and remove "sudo";
# if you want to upgrade the versions already present in the system, also add --upgrade
sudo pip3 install tornado
sudo pip3 install pymongo
git clone https://github.com/raspibo/ibt2
cd ibt2
```

Installation of [Node.js](https://nodejs.org/en/download/) and npm is left as an exercise to the reader.

To run it:
``` bash
# install dependencies (one time only, or every time the dependencies in package.json change)
npm install

# build for production with minification (each time the sources changes)
npm run build

# run the Python webserver at localhost:3000
npm run server
```

Now you can **point your browser to [http://localhost:3000/](http://localhost:3000/)** (that's the server for production)

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
python3 ./tests/ibt2_tests.py
```

Your browser will automatically open [http://localhost:8080/](http://localhost:8080/) (that's the server for development)


Development
===========

See the *docs/DEVELOPMENT.md* file for more information about how to contribute.


Technological stack
===================

- [VueJS](https://vuejs.org/) for the webApp
- [Vue Material](https://vuematerial.github.io/) for the UI components
- [Vue Datepicker](https://github.com/charliekassel/vuejs-datepicker) for the datepicker
- [Vue Markdown](https://www.npmjs.com/package/vue-markdown) for parsing the Markdown syntax
- [Tornado web](http://www.tornadoweb.org/) as web server
- [MongoDB](https://www.mongodb.org/) to store the data
- [Python 3](https://www.python.org/) is required

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

