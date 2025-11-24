# Architecture — QA Automation Portfolio

This repo demonstrates how I structure UI + API automation for hiring
managers and recruiters. Real client work is under NDA; the structure and
practices here match what I use on projects.

## High-level components

- **UI tests** (`autotests/`)
  - pytest tests that exercise user flows (Azercell login).
  - Small, readable tests that delegate UI details to Page Objects.

- **Page Objects** (`pages/`)
  - Encapsulate locators and actions for each page.
  - Common behaviour lives in `BasePage` (click with retries, window switch).

- **Fixtures & configuration** (`conftest.py`, `pytest.ini`)
  - WebDriver lifecycle (Chrome/Chromium, headless via `HEADLESS`).
  - Shared `wait` fixture for explicit waits.
  - `phone_number` fixture via `AZERCELL_PHONE` env or `--phone-number`.
  - Screenshot + HTML capture on failure to `reports/`.

- **Utilities** (`utils/`)
  - Small pure functions like `normalize_phone_number()` with unit tests.

- **API tests** (`postman/`)
  - Postman collections for Restful Booker.
  - Newman runs in CI, producing HTML + JUnit reports.

- **CI** (`.github/workflows/ci.yml`)
  - `lint` → `ui-tests` → `api-tests` jobs.
  - Chrome is installed with `browser-actions/setup-chrome`.
  - Artifacts (screenshots, HTML, JUnit, Newman HTML) are uploaded.

- **Documentation** (`docs/`)
  - `test_strategy.md` — overall approach & CI gating.
  - `test_cases_azercell_login.md` — documented scenarios with IDs.
  - `traceability_matrix.md` — mapping AZ-LG-* → tests.
  - `adr/*` — small Architecture Decision Records.

## Configuration & environments

- **Env vars**
  - `AZERCELL_PHONE` / `PHONE_NUMBER`: live phone used in UI flows.
  - `HEADLESS`: `1`/`0` or `true`/`false` (defaults to headless).
  - `REPORTS_DIR`: optional custom reports directory.
- **CLI**
  - `pytest --phone-number=507475560`
  - Markers: `-m smoke`, `-m "smoke and not slow"` etc.

No secrets are committed. Any real phone numbers / credentials must come
from local `.env` (git-ignored) or CI secrets.

## Extending

To add new UI automation:

1. Add a Page Object in `pages/` for the feature.
2. Add test cases to `docs/test_cases_*.md` with IDs.
3. Implement tests under `autotests/`, marking them with `@pytest.mark.testcase`.
4. Wire into traceability matrix and, if needed, smoke vs regression groups.