## Azercell Login UI Tests

Selenium-based test automation for the Azercell “Kabinetim” login flow
using Python and pytest.

### Prerequisites

- Python 3.11+ (Python 3.14 also works)
- Google Chrome installed locally
- Recommended: a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Chromedriver is managed automatically via `webdriver-manager` and the
Selenium manager; you do not need to install it manually.

### Configuring the phone number

Some tests interact with the live Azercell login form and require a
**real Azercell mobile number**. The `phone_number` fixture in
`conftest.py` picks the first available value in this order:

1. Pytest CLI option: `--phone-number` (or `--phone`)
2. Environment variable: `AZERCELL_PHONE`
3. Environment variable: `PHONE_NUMBER`

If no value is set, or if the value is the placeholder `5XXXXXXXXX`,
tests that require a real number will automatically **skip** with a
clear message.

**Recommended formats**

- Use: `5XXXXXXXXX` (no leading `0` or country code)
- The helper `normalize_phone_number()` will handle spaces, dashes and
  optional leading `0`.

**Examples**

- Environment variables:

```bash
export AZERCELL_PHONE="5012345678"
export HEADLESS="1"          # "0" to see the browser
export TEST_ENV="local"
```

- `.env` file (auto-loaded via `python-dotenv`):

```text
AZERCELL_PHONE=5012345678
HEADLESS=1
TEST_ENV=local
```

- Command line:

```bash
pytest autotests --phone-number=5012345678 -m "smoke or regression" -v
```

### Useful environment variables

From `conftest.py` and `AzercellLoginPage`:

- `TEST_ENV`  
  Logical environment name (`local`, `ci`, etc.).

- `AZERCELL_BASE_URL` / `BASE_URL`  
  Marketing site base URL.  
  Default in code: `https://www.azercell.com/az/`  
  CI overrides via `BASE_URL`, e.g. `https://www.azercell.com/en`.

- `AZERCELL_LOGIN_URL`  
  Direct login URL.  
  Default: `https://kabinetim.azercell.com/login`.

- `AZERCELL_PHONE` / `PHONE_NUMBER`  
  Real Azercell phone for login flows (format `5XXXXXXXXX`).  
  If missing or set to `5XXXXXXXXX`, deeper login tests skip.

- `HEADLESS`  
  `"1"` / `"true"` / `"yes"` → headless mode (default).  
  `"0"` / `"false"` → visible browser.

- `REUSE_BROWSER`  
  `"1"` → reuse a single browser per test session.  
  `"0"` (default) → new browser per test function.

- `WAIT_TIMEOUT`  
  Explicit wait timeout (seconds). Default: `15`.

- `PAGE_LOAD_TIMEOUT`  
  Page load timeout (seconds). Default: `45`.

- `REPORTS_DIR`  
  Root directory for reports. Default: `./reports`.

### Quick start

Run all UI tests:

```bash
pytest autotests -v
```

Run only the Azercell login page tests:

```bash
pytest autotests/test_azercell_login_page.py -v
```

Run only smoke tests (fastest, used in CI):

```bash
pytest autotests -m smoke -v
```

Run a specific test:

```bash
pytest autotests/test_azercell_login_page.py::test_complete_flow_to_otp_page -v
```

### What gets reported on failure

When a UI test fails, the `pytest_runtest_makereport` hook in
`conftest.py` saves:

- Screenshot:
  `reports/screenshots/<test_nodeid>_<timestamp>.png`
- Page source:
  `reports/screenshots/<test_nodeid>_<timestamp>.html`

In CI, these are uploaded as part of the `ui-test-artifacts` artifact.

### Files of interest

- `autotests/test_azercell_login_page.py` — main Azercell login
  scenarios (smoke + regression)
- `autotests/test_smoke.py` — compact smoke test for direct login access
- `pages/azercell_login_page.py` — Page Object for Azercell login flows
- `pages/base_page.py` — shared helpers (`open()`, robust `click()`,
  window switching)
- `conftest.py` — fixtures: `browser`, `wait`, `phone_number`,
  screenshot-on-failure hook, environment logging
- `pytest.ini` — pytest markers and default configuration

### Notes for reviewers / recruiters

- By default, tests that require a real registered number are **safe**:
  they auto‑skip unless a non‑placeholder phone is provided.
- In CI, the phone number is read from `PHONE_NUMBER`, which must be
  injected via a GitHub Actions secret (e.g. `AZERCELL_PHONE_NUMBER`).
- The suite demonstrates:
  - Page Object Model
  - Robust locators and fallbacks
  - Environment-aware configuration via env vars / `.env`
  - Diagnostics via screenshots and HTML capture on failure.