# ibt2 - I'll be there, 2

**I'll be there, 2** is an oversimplified application to register attendees at a conference or event.

## Run, develop and debug

To run it:
``` bash
# install dependencies (one time only)
npm install

# build for production with minification (one time only)
npm run build

# run the Python webserver at localhost:3000
npm run server
```

To run a development environment:
``` bash
# install dependencies (one time only)
npm install

# run the Python web server using a testing database
npm run devserver &

# serve with hot reload at localhost:8080
npm run dev
```

Technological stack
===================

- [VueJS](https://vuejs.org/) for the webApp
- [Vue Material](https://vuematerial.github.io/) for the UI components
- [Tornado web](http://www.tornadoweb.org/) as web server
- [MongoDB](https://www.mongodb.org/) to store the data

The web part is incuded; you need to install Tornado, MongoDB and the pymongo module on your system (no configuration needed).


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

