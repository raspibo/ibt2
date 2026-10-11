# Frontend regression check

The app uses Vite with Vue 3's migration runtime. Vue Material 0.7, Vue Router 2,
Vuex 2, and the date picker still require Vue 2 compatibility. Both the runtime
alias and `template.compilerOptions.compatConfig.MODE: 2` in `vite.config.mjs`
are intentional. This is not yet a complete migration to native Vue 3 components.
See the [Vue migration build guide](https://v3-migration.vuejs.org/migration-build.html).

Keep inputs and leading icons directly inside Material input containers. Extra
`span` wrappers change flex sizing and break icon and label sibling selectors.
Native keyboard listeners on legacy inputs use `.native` with the compatibility
compiler.
The wrapper in `IbtDialog.vue` keeps a stable DOM anchor when Material moves its
dialog root to `document.body`; otherwise Vue 3 can fail when inserting the
attendee editor beside it.

`IbtMenuItem.vue` replaces the legacy menu item's functional list renderer, which
relies on Vue 2's `data.on` to decide whether a row is clickable.
`IbtMenuContent.vue` provides arrow-key navigation using the rendered buttons.
Menu actions activate on keyup so the Enter used to open an editor does not also
submit the newly focused input.

Run the production build:

```sh
npm run build
```

The browser smoke test intercepts API requests and uses in-memory fixtures. It
needs no Python server, database, or real credentials. It verifies input geometry,
keyboard login, password visibility, adding/editing attendees, creating a group,
day-note dialogs, settings switches, profile saving, logout, and responsive layout
at desktop, tablet, and phone widths. It also fails on browser runtime errors.

Playwright is pinned in the project's development dependencies and lockfile.
Install the dependencies and matching Chromium browser:

```sh
npm ci --legacy-peer-deps
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
