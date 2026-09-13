# ibt2 — I'll Be There, 2

**I'll Be There, 2** is a deliberately simple application for registering attendance at a conference or other event.

Typical workflow:

- Sign in if you want to protect the entries you create. Enter a new username and password to create an account.
- Choose a date.
- Select an existing group or enter the name of a new one.
- Add your name and, optionally, a note.

Only an entry's owner or an administrator can edit or delete it. On first startup, ibt2 creates an `admin` account. Pass `--admin_password` (or the same container argument) to choose its initial password. Otherwise, a random password is written to the server log. Change it from the personal page after signing in.

Notes support [Markdown](https://daringfireball.net/projects/markdown/).

## Run with Docker Compose

Docker Compose is the recommended way to run ibt2. It starts ibt2 and MongoDB with persistent storage:

```sh
docker compose up --build
```

Open [http://localhost:3000/](http://localhost:3000/). Stop the stack with `docker compose down`. The MongoDB data is stored in the `data` volume; do not remove that volume unless you intend to delete all attendance data.

See [the Docker guide](docs/DOCKER.md) for backup, restore, and administrator-password instructions.

## Run without Docker

You need Node.js 20.19+ (or 22.12+), Python 3, and a reachable MongoDB instance. Create a virtual environment and install the Python dependencies:

```sh
git clone https://github.com/raspibo/ibt2.git
cd ibt2
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install tornado pymongo
npm ci --legacy-peer-deps
```

Build the frontend and start the server:

```sh
npm run build
python ibt2.py --mongo_url=mongodb://localhost
```

Then open [http://localhost:3000/](http://localhost:3000/). To enable HTTPS, place `ibt2_key.pem` and `ibt2_cert.pem` in the `ssl/` directory before starting the server.

## Development

Install dependencies as above, then start the backend and Vite development server in separate terminals:

```sh
# Terminal 1: use the test database
npm run devserver
```

```sh
# Terminal 2: Vite dev server at http://localhost:8080/
npm run dev
```

Run the backend tests while the development backend is running:

```sh
python3 tests/ibt2_tests.py
```

See [the development guide](docs/DEVELOPMENT.md) and [the frontend regression-check guide](docs/UI-TESTING.md) for details.

## Technology

- [Vue 3](https://vuejs.org/) with the Vue 2 compatibility build during the migration
- [Vue Material](https://vuematerial.github.io/) UI components
- [vuejs-datepicker](https://github.com/charliekassel/vuejs-datepicker)
- [marked](https://www.npmjs.com/package/marked) for Markdown rendering
- [Tornado](https://www.tornadoweb.org/) web server
- [MongoDB](https://www.mongodb.com/) data store

## Other projects

For a more complete event-management application with ticket support, see [EventMan(ager)](https://github.com/raspibo/eventman).

## License and copyright

Copyright 2016–2026 Davide Alberani <da@mimante.net>, RaspiBO <info@raspibo.org>

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
