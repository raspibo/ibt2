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
- /#/user/:user - show setting for the give user ID

Web server
----------

Database layout
===============

Information are stored in MongoDB.  Whenever possible, object are converted into native ObjectId.

attendees collection
--------------------


Code layout
===========

The code is so divided:

    +- ibt2.py - the Tornado Web server


Coding style and conventions
----------------------------

It's enough to be consistent within the document you're editing.

I suggest four spaces instead of tabs for all the code: Python (**mandatory**), JavaScript, HTML and CSS.

Python code documented following the [Sphinx](http://sphinx-doc.org/) syntax.


not-so-FAQs
===========

