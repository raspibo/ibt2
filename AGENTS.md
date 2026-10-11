# Repository Guidelines

## Project Structure & Module Organization

`src/` contains the Vue 3 frontend: PascalCase `.vue` components, `main.js`, Vuex state in `store.js`, Fetch helpers in `api.js`, and shared CSS. `static/` holds assets; `dist/` is generated production output. The Tornado backend lives in `ibt2.py`, with utilities in `utils.py` and the project-owned MongoDB connector `monco.py`. Keep `monco.py` internal. Tests live in `tests/`; development and deployment instructions live in `docs/`. Root Docker files define the current container workflow.

## Build, Test, and Development Commands

Use Node 22.12+ with npm 10+, Python 3.11+, and MongoDB.

- `npm ci`: install locked frontend dependencies.
- `python -m pip install --require-hashes -r requirements-dev.txt`: install runtime and backend test dependencies in a virtual environment.
- `npm run devserver`: start the backend using `ibt2_test`.
- `npm run dev`: serve the frontend at port 8080; run alongside the backend.
- `npm run build`: produce `dist/` using Vite.
- `npx --no-install playwright-core install chromium`: install the matching test browser.
- `npm run test:ui`: test a temporary production preview; build first.
- `npm run test:backend`: start a temporary backend and run integration tests.
- `docker compose up --build`: build and run the application with MongoDB.

## Coding Style & Naming Conventions

Use four spaces and follow surrounding conventions. Python functions generally use snake_case; JavaScript uses camelCase. Keep Vue component filenames PascalCase and application CSS classes prefixed `ibt-`. Use Sphinx-style Python docstrings. No dedicated formatter or linter is configured. Keep Markdown sanitization and HTTP error handling intact; update Vite proxy routes when adding backend endpoints.

## Testing Guidelines

Backend tests use `unittest` in `tests/ibt2_tests.py`, with `test_*` methods. Browser checks use Playwright and Node assertions in `tests/ui-smoke.cjs`. No coverage percentage is enforced. Validate affected behavior and responsive layouts; CI also checks Docker packaging and Python 3.11/3.14. Backend tests delete collections in `ibt2_test`: use disposable MongoDB and set `IBT2_TEST_MONGO_URL` appropriately.

## Commit & Pull Request Guidelines

History uses short, action-oriented subjects, without a mandatory prefix: `Keep wrapped groups beside the calendar`. Keep changes focused. Describe the problem, resulting behavior, and checks run in pull requests. Link relevant issues and include screenshots for visual changes.

## Dependencies & Configuration

Use external packages rather than copied upstream sources. Commit `package-lock.json` updates with dependency changes. Regenerate hashed Python locks from `.in` files, runtime first, following `docs/DEVELOPMENT.md`. Never commit credentials or TLS keys. Change the default administrator password before deployment.
