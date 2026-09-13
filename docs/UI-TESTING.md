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

Install the browser test tools separately from application dependencies:

```sh
npm install --prefix /tmp/ibt2-ui-tools playwright-core
/tmp/ibt2-ui-tools/node_modules/.bin/playwright-core install chromium
```

Start Vite in one terminal, then run the check in another:

```sh
npm run dev -- --host 127.0.0.1 --port 8081
```

```sh
NODE_PATH=/tmp/ibt2-ui-tools/node_modules node tests/ui-smoke.cjs
```

Set `IBT2_UI_URL` to test another local port or a Vite preview of the production
build. These checks validate frontend behavior against the mocked API contract;
they do not replace backend integration tests.
