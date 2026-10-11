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
src/api.js       Browser Fetch helpers for the REST API
src/style.css    Application layout and shared styles
monco.py         MongoDB connector
utils.py         Shared utilities
dist/            Production build output
src/             Frontend source
  main.js        Frontend entry point
  App.vue        Main component
  *.vue          Other frontend components
  store.js       Shared frontend state
```

## Python dependencies

`requirements.in` declares supported runtime dependency ranges. The generated
`requirements.txt` pins runtime dependencies, including transitive dependencies,
with artifact hashes. Local installation and Docker use this same lock.
`requirements-dev.in` adds backend test dependencies and constrains runtime
versions to the runtime lock; `requirements-dev.txt` locks the combined environment.
Install it with:

```sh
python -m pip install --require-hashes -r requirements-dev.txt
```

`monco.py` is an internal module maintained here. The `bson` module is provided by
PyMongo; do not install the separate `bson` distribution.

To update the locks, use a separate tooling virtual environment:

```sh
python3 -m venv /tmp/ibt2-lock-tools
/tmp/ibt2-lock-tools/bin/python -m pip install pip-tools==7.6.2
/tmp/ibt2-lock-tools/bin/pip-compile --upgrade --generate-hashes --strip-extras --no-emit-index-url --no-emit-trusted-host --output-file=requirements.txt requirements.in
/tmp/ibt2-lock-tools/bin/pip-compile --upgrade --generate-hashes --strip-extras --no-emit-index-url --no-emit-trusted-host --output-file=requirements-dev.txt requirements-dev.in
```

Regenerate runtime first, then development. Review both diffs and verify clean
installations on the supported Python versions before committing an update.
Locks cover the default dependencies; platform-specific wheel selection still
depends on the Python version and operating system.

## Automated checks

Use npm 10 or newer for dependency installation, matching the Node 22 Docker
build and CI environment.

The frontend runs native Vue 3 with Router 4 and Vuex 4. Interactive controls use
the MIT-licensed PrimeVue 4 line; its theme and icon packages are also external
npm dependencies. Route components are loaded on demand. Roboto imports include
only the Latin subset at weights 400, 500, and 700. HTTP failures reject before
successful-update callbacks, preserving drafts when a write fails. Markdown HTML
is sanitized with DOMPurify before rendering.

`npm run test:ui` starts a production preview and runs the browser smoke checks;
first build the frontend and install Chromium as described in [UI testing](UI-TESTING.md).

`npm run test:backend` starts a backend on port 3001, runs the existing integration
tests, and stops the backend. It requires `requirements-dev.txt` and a reachable
MongoDB instance. The tests delete collections in `ibt2_test`; use a disposable
database instance. For example, in separate terminals:

```sh
docker run --rm --name ibt2-test-mongo -p 127.0.0.1:27018:27017 mongo:7.0
```

```sh
IBT2_TEST_MONGO_URL=mongodb://127.0.0.1:27018 npm run test:backend
```

Stop the MongoDB container with `docker stop ibt2-test-mongo` when finished. It
has no persistent volume. Set `IBT2_TEST_PORT` to change the backend runner port.
The test database name remains `ibt2_test`.

GitHub Actions runs production browser checks, backend tests on Python 3.11 and
3.14 with fresh MongoDB service containers, and Docker build and packaging checks
on pushes and pull requests. Actions are pinned to commit hashes. A successful
version-tag run can publish the container as described in [Docker](DOCKER.md).

## Style

Follow the style of the file you are changing. Use four spaces rather than tabs for Python (required), JavaScript, HTML, and CSS. Python docstrings use [Sphinx](https://www.sphinx-doc.org/) field-list syntax.

## FAQ

**Why is the backend not written in Node.js?**

Because the original Tornado backend already existed and remains a good fit for this small service.

**What are `.vue` files?**

They are [Vue single-file components](https://vuejs.org/guide/scaling-up/sfc.html). Vite compiles them for the browser.

**I added a backend route and the Vite development server cannot reach it.**

Add the route to `server.proxy` in `vite.config.mjs`.
