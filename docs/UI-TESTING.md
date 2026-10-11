# Frontend regression check

The frontend uses native Vue 3, Vue Router 4, Vuex 4, and PrimeVue 4. There is
no Vue 2 compatibility runtime. PrimeVue supplies the calendar, inputs, switches,
menus, dialogs, and messages; page layouts use ordinary HTML and application CSS.

`IbtMenu.vue` and `IbtPrompt.vue` configure external PrimeVue controls for the
application's actions and note editors. HTTP requests use browser Fetch through
`src/api.js`, with encoded path parameters and explicit rejection of failed HTTP
responses. Markdown is rendered with marked and sanitized with DOMPurify.

Run the production build:

```sh
npm run build
```

The browser smoke test intercepts API requests and uses in-memory fixtures. It
needs no Python server, database, or real credentials. It verifies input geometry,
keyboard login, password visibility, adding/editing attendees, failed API writes,
group creation/renaming/deletion and notes, day-note dialogs, calendar navigation,
browser history, settings switches, user navigation, profile saving, sanitized
Markdown, logout, and responsive layout at desktop, tablet, and phone widths.
It also fails on browser runtime errors and Vue component warnings.

Playwright is pinned in the project's development dependencies and lockfile.
Install the dependencies and matching Chromium browser:

```sh
npm ci
npx --no-install playwright-core install chromium
```

Build the frontend and run the automated check. The runner starts and stops a
local Vite preview of the production build:

```sh
npm run build
npm run test:ui
```

```sh
IBT2_UI_URL=http://127.0.0.1:8080 node tests/ui-smoke.cjs
```

The command above runs the smoke test directly against an already running server.
Set `IBT2_UI_PORT` to change the automated preview's port (default 8081).
On Linux, use `npx --no-install playwright-core install --with-deps chromium`
if browser system libraries are missing; CI uses this command.
These checks validate frontend behavior against the mocked API contract;
they do not replace backend integration tests.
