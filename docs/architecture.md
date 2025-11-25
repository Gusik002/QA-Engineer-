# Architecture — QA Automation Portfolio

This repository demonstrates how I structure UI, API and performance
automation for hiring managers and recruiters. Real client work is under
NDA; the structure and practices here mirror what I use on projects.

## High-level components

- **UI tests** (`autotests/`)
  - pytest tests that exercise Azercell login flows and additional smoke
    checks.
  - Small, readable tests that delegate browser interaction to Page
    Objects.
  - Markers group tests into `smoke`, `regression` and `slow`.

- **Page Objects** (`pages/`)
  - Encapsulate locators and actions for each page under test.
  - `AzercellLoginPage` implements Kabinetim login flows and wraps:
    - Home page navigation
    - Login button click with fallbacks
    - Phone input and submission
    - OTP and password-change flows (where available).
  - Shared behaviour in `BasePage`:
    - `open()` for navigation
    - Robust `click()` with retries and JS fallback
    - Window/tab switching.

- **Fixtures & configuration** (`conftest.py`, `pytest.ini`)
  - WebDriver lifecycle (Chrome, typically headless in CI).
  - `browser` fixture:
    - Per-test browser by default.
    - Optional session-wide reuse via `REUSE_BROWSER=1`.
  - `wait` fixture for explicit waits (configurable via `WAIT_TIMEOUT`).
  - `phone_number` fixture:
    - Reads CLI option `--phone-number`/`--phone` or env vars
      `AZERCELL_PHONE` / `PHONE_NUMBER`.
    - Uses `5XXXXXXXXX` as a safe placeholder; tests that require a real
      number auto-skip when the placeholder is detected.
  - Screenshot + HTML capture on failure into `reports/screenshots/`.
  - Environment banner logged at the start of each run (env name, base
    URL, timeouts, masked phone).

- **Utilities** (`utils/`)
  - Small pure helpers such as `normalize_phone_number()`.
  - These are exercised both via UI tests and, where useful, via unit
    tests.

- **API tests** (`postman/`)
  - Postman collections for the public Restful Booker API.
  - Environment files under `postman/environments/`.
  - Newman runs in CI to produce HTML and JUnit XML reports.

- **Performance smoke** (`performance/`)
  - k6 script (`restful-booker-smoke.js`) exercising core Restful Booker
    endpoints under a small load, suitable for nightly/regression.

- **CI configuration** (`.github/workflows/ci.yml`)
  - GitHub Actions workflow `QA Portfolio CI` with jobs:
    - `lint` — runs `ruff` and `black` on `pages` and `autotests`.
    - `ui-tests` — installs Google Chrome via `apt`, then runs pytest
      smoke (`-m "smoke"`) on push/PR and smoke+regression on nightly
      schedules.
    - `api-tests` — runs Newman against the Restful Booker collection
      and uploads HTML + JUnit reports.
    - `perf-smoke` — runs the k6 smoke script on schedule or manual
      trigger.
  - UI job uploads screenshots, page source and JUnit XML as artifacts.

- **Documentation** (`docs/`)
  - `test_strategy.md` — overall approach, pyramid, CI gating.
  - `test_cases_azercell_login.md` — documented Azercell login
    scenarios with IDs (AZ‑LG‑*).
  - `traceability_azercell_login.md` — mapping AZ‑LG‑* test cases to
    automated tests.
  - `onboarding_guide_for_new_qa.md` — how a new QA can get productive.
  - `adr/*` — lightweight Architecture Decision Records (if present).

## Configuration & environments

### Environment variables (UI)

Key environment variables used by the UI layer:

- `TEST_ENV`  
  Logical environment name (e.g. `local`, `ci`). Logged at test start.

- `AZERCELL_BASE_URL` / `BASE_URL`  
  Marketing site base URL used for the Azercell home page.  
  Defaults in code to `https://www.azercell.com/az/`.  
  CI sets `BASE_URL=https://www.azercell.com/en`.

- `AZERCELL_LOGIN_URL`  
  Direct login URL (Kabinetim).  
  Defaults to `https://kabinetim.azercell.com/login`.

- `AZERCELL_PHONE` / `PHONE_NUMBER`  
  Real phone number for Azercell login flows. Expected format:
  `5XXXXXXXXX` (no leading `0` or `+994`).  
  If missing or set to `5XXXXXXXXX`, tests that require a real number
  skip automatically.

- `HEADLESS`  
  `"1"`, `"true"`, `"yes"` → headless Chrome (default).  
  `"0"`, `"false"` → visible Chrome window for local debugging.

- `REUSE_BROWSER`  
  `"1"` → a single session-scoped driver reused across tests.  
  `"0"` (default) → new driver per test function.

- `WAIT_TIMEOUT`  
  Explicit wait timeout in seconds (default `15`).

- `PAGE_LOAD_TIMEOUT`  
  Page load timeout in seconds (default `45`).

- `REPORTS_DIR`  
  Root directory for reports. Defaults to `./reports`.  
  CI sets `reports/ui` for UI and `reports/api` for API.

Secrets (such as real phone numbers) are never committed; they must be
provided via local `.env` (git-ignored) or CI secrets.

### CI secrets

For the Azercell login flows in CI:

- GitHub Actions secret `AZERCELL_PHONE_NUMBER` is injected as
  `PHONE_NUMBER` into the `ui-tests` job.
- This allows the same test code to run both:
  - safely without a real number (regression tests auto-skip), and
  - fully against a live number in controlled environments.

## Extending

### Adding new UI automation

1. **Create or extend a Page Object** in `pages/`:
   - Inherit from `BasePage`.
   - Encapsulate locators and high-level actions.
   - Keep Selenium details out of the test functions.

2. **Add or update test cases** in `docs/test_cases_*.md`:
   - Assign IDs (e.g. `AZ-LG-0XX`).
   - Capture preconditions, steps, expected results and priorities.

3. **Implement tests** under `autotests/`:
   - Use fixtures (`browser`, `wait`, and any page-specific fixtures).
   - Mark with `@pytest.mark.smoke`, `@pytest.mark.regression` or
     `@pytest.mark.slow` as appropriate.
   - Optionally tag with `@pytest.mark.testcase("AZ-LG-0XX")` for
     traceability.

4. **Update traceability**  
   Add or adjust rows in the relevant traceability matrix
   (`docs/traceability_*.md`) so each important case maps to at least
   one automated test.

5. **Run locally**  
   - For quick feedback: `pytest autotests -m smoke -v`.
   - For deeper coverage: `pytest autotests -m "smoke or regression" -v`.

6. **Ensure CI passes**  
   Push your branch and confirm the `lint`, `ui-tests` and `api-tests`
   jobs succeed.

This structure keeps UI automation maintainable, observable and easy to
reason about while staying realistic enough to showcase production-ready
practices.