# ibt2 development

## Routes

The frontend uses hash-based client-side routing. Navigation does not make an HTTP request unless the page fetches or changes data.

| Route | Purpose |
| --- | --- |
| `/#/` | Home page; redirects to the current day. |
| `/#/day/:day` | Groups for a date in `yyyy-mm-dd` format. |
| `/#/user/` | User list; administrators only. |
| `/#/user/:id` | Settings for one user. |
| `/#/settings/` | Global settings; administrators only. |

## HTTP API

| Endpoint | Methods | Purpose |
| --- | --- | --- |
| `/attendees` | `GET`, `POST` | List or create attendees. |
| `/attendees/:id` | `GET`, `PUT`, `DELETE` | Read, update, or delete one attendee. |
| `/days` | `GET` | List entries grouped by day and group. |
| `/days/:day` | `GET` | Read one day's entries, grouped by group. |
| `/days/:day/info` | `PUT` | Create or update a day's information. |
| `/days/:day/groups/:group` | `PUT`, `DELETE` | Rename or delete a group. `PUT` accepts `newName`. |
| `/days/:day/groups/:group/info` | `PUT` | Create or update group information. |
| `/users` | `GET`, `POST` | List or create users. |
| `/users/:id` | `GET`, `PUT` | Read or update a user. |
| `/users/current` | `GET` | Read the currently signed-in user. |
| `/settings` | `GET`, `POST`, `PUT` | Read, create, or update global settings. |
| `/login` | `POST` | Sign in. |
| `/logout` | `GET` | Sign out. |

Example attendee response:

```json
{"day":"2017-01-20","name":"Attendee Name","group":"Group Name","updated_by":"587a7c79dff0d71c89211dc4","created_at":"2017-01-20 13:57:26.029000","updated_at":"2017-01-20 13:57:26.029000","created_by":"587a7c79dff0d71c89211dc4","_id":"58820936dff0d740dee647a4"}
```

Example day response:

```json
{"day":"2017-01-20","groups":[{"group":"Group Name","attendees":[{"day":"2017-01-20","name":"Attendee Name","group":"Group Name","updated_by":"587a7c79dff0d71c89211dc4","created_at":"2017-01-20 13:57:26.029000","updated_at":"2017-01-20 13:57:26.029000","created_by":"587a7c79dff0d71c89211dc4","_id":"58820936dff0d740dee647a4"}]}]}
```

## Project layout

```text
ibt2.py          Tornado web server
index.html       HTML entry point
vite.config.mjs  Vite configuration
monco.py         MongoDB connector
utils.py         Shared utilities
dist/            Production build output
src/             Frontend source
  main.js        Frontend entry point
  App.vue        Main component
  *.vue          Other frontend components
  store.js       Shared frontend state
```

## Style

Follow the style of the file you are changing. Use four spaces rather than tabs for Python (required), JavaScript, HTML, and CSS. Python docstrings use [Sphinx](https://www.sphinx-doc.org/) field-list syntax.

## FAQ

**Why is the backend not written in Node.js?**

Because the original Tornado backend already existed and remains a good fit for this small service.

**What are `.vue` files?**

They are [Vue single-file components](https://vuejs.org/guide/scaling-up/sfc.html). Vite compiles them for the browser.

**I added a backend route and the Vite development server cannot reach it.**

Add the route to `server.proxy` in `vite.config.mjs`.
