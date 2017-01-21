ibt2 development
================

Paths
=====

Webapp
------

These are the paths you see in the browser (VueJS does client-side routing: no request is issued to the web server, during navigation, if not for fetching data and issuing commands):

- / - home; will redirect to the entry for today
- /#/day/:day - show groups for the given date (in yyyy-mm-dd format)
- /#/user/ - list of all users (only visible by admins)
- /#/user/:id - show setting for the give user ID

Web server
----------

- /attendees GET - the list of all entries
- /attendees POST - write a new entry
- /attendees/:id GET - a single entry
- /attendees/:id PUT - update an entry
- /days GET - all entries, grouped by day and by group
- /days/:day GET - a single day entries, grouped by group (yyyy-mm-dd format)
- /users GET - list of all users
- /users POST - create a new user
- /users/:id GET - a single user
- /users/:id PUT - update a user
- /users/current GET - information about the currently logged in user
- /login POST - login of a user
- /logout GET - log the current user out

Example of */attendees/:id*:
``` json
{"day": "2017-01-20", "name": "Attendee Name", "group": "Group Name", "updated_by": "587a7c79dff0d71c89211dc4", "created_at": "2017-01-20 13:57:26.029000", "updated_at": "2017-01-20 13:57:26.029000", "created_by": "587a7c79dff0d71c89211dc4", "_id": "58820936dff0d740dee647a4"}
```

Example of */days/:day*:
``` json
{"day": "2017-01-20", "groups": [{"name": "Group Name", "attendees": [{"day": "2017-01-20", "name": "Attendee Name", "group": "Group Name", "updated_by": "587a7c79dff0d71c89211dc4", "created_at": "2017-01-20 13:57:26.029000", "updated_at": "2017-01-20 13:57:26.029000", "created_by": "587a7c79dff0d71c89211dc4", "_id": "58820936dff0d740dee647a4"}]}]}
```


Database layout
===============

Information are stored in MongoDB.  The *_id* key values are converted into native ObjectId.

The main information are stored in the *attendees* collection.


Code layout
===========

The code is so divided:

    +- ibt2.py - the Tornado Web server
    +- index.html - the html page that will be injected with the webApp
    +- monco.py - backend to connect to a MongoDB instance
    +- utils.py - various utilities
    +- build/ - webpack and node configuration
    +- dist/ - output of the build command will be put here
    +- src/ - webApp sources
       |
       +- main.js - kickoff the VueJS webApp
       +- App.vue - main component of the webApp
       +- *.vue - other webApp components
       +- state.js - shared state of the webApp


Coding style and conventions
----------------------------

It's enough to be consistent within the document you're editing.

I suggest four spaces instead of tabs for all the code: Python (**mandatory**), JavaScript, HTML and CSS.

Python code documented following the [Sphinx](http://sphinx-doc.org/) syntax.


not-so-FAQs
===========


- **Q:** why the backend is not in Node.js? Why?! WHYYY!?!!?!
- **A:** because science! (but mostly because I already had most of it ready from other projects)


- **Q:** will it ever be ported to Python 3?
- **A:** yes, probably in the near future.


- **Q:** *.vue* files? What's that?
- **A:** Vue [single-file components](https://vuejs.org/v2/guide/single-file-components.html); a [webpack](https://webpack.js.org/) plugin will take care of translating them into stuff that can be digested by a browser.

- **Q:** I've added a new path to the backend, and now the hot reload server is not working!!1!!
- **A:** that's not even a question.  Anyway, add the path to dev.proxyTable in *config/index.js*


- **Q:** will it be integrated with Slack?
- **A:** hell, no.
