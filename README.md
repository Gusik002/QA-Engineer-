# QA Automation Portfolio – Huseyn Gasimov

This repo is a **public, production‑style example** of how I design and
build test automation: UI, API, performance and CI/CD. Real client work
is under NDA, but the structure, patterns and documentation here match
what I use on real projects.

---

## If you only have 60 seconds

Look at these first:

1. **How I structure automation**
   - `docs/architecture.md`
   - `docs/test_strategy.md`

2. **How tests map to requirements**
   - `docs/traceability_matrix.md`
   - `docs/test_cases_azercell_login.md`

3. **Concrete UI automation (Selenium + pytest)**
   - Tests: `autotests/test_azercell_login_page.py`,
     `autotests/test_smoke.py`
   - Page Objects: `pages/azercell_login_page.py`, `pages/base_page.py`

4. **API + performance examples**
   - API: `postman/collections/restful-booker.postman_collection.json`
   - Performance: `performance/restful-booker-smoke.js`

5. **Process / onboarding**
   - `docs/onboarding_guide_for_new_qa.md`

If you skim only a few files, those will give you an accurate view of
how I work.

---

## What this repository demonstrates

### 1. Cross‑layer testing

- **Web UI**  
  Azercell “Kabinetim” login flow automated with:
  - Python, `pytest`
  - Selenium WebDriver
  - Page Object Model (POM)
- **API**  
  Restful Booker API tested with:
  - Postman collections
  - Newman CLI (HTML + JUnit reports)
- **Performance smoke**  
  Light k6 script against Restful Booker to show how I wire basic
  performance checks into CI.

### 2. CI‑first mindset

- GitHub Actions workflow: `.github/workflows/ci.yml`
- On every **push** and **pull request**:
  - `lint` job runs `ruff` + `black` as a quality gate
  - `ui-tests` job runs Selenium smoke tests in headless Chrome
  - `api-tests` job runs the Postman collection via Newman
- **Nightly schedule**:
  - UI: smoke + regression pack
  - API: full collection
  - Performance: k6 smoke test
- All jobs publish artifacts (JUnit XML, screenshots, HTML, Newman
  reports) to make debugging straightforward.

### 3. Risk‑based test design

- Focus on **small, reliable smoke suites** that protect the most
  important flows:
  - Azercell home page reachable
  - Login button navigates correctly
  - Phone input works and validates
- Deeper **regression** tests:
  - Additional navigation rules
  - Password‑change flow (when available)
  - Format variations and validation behaviour

### 4. Maintainable automation

- Clear separation of concerns:
  - Tests live in `autotests/`
  - Page Objects live in `pages/`
  - Utilities in `utils/`
  - Configuration and fixtures in `conftest.py`
- Page Objects hide Selenium details behind readable methods like:
  - `open_home_page()`
  - `click_login_button()`
  - `enter_phone_number()`
  - `submit_phone_number()`
- Robustness features:
  - Multiple locators and fallbacks for key elements
  - Centralised `BasePage.click()` with retries and JS fallback
  - Window/tab switching when the site opens login in a new window
  - Automatic screenshots and HTML capture on test failure

### 5. Engineering discipline

- Linters and formatters:
  - `ruff` for static analysis
  - `black` for formatting
- Pre‑commit configuration:
  - `.pre-commit-config.yaml` to keep the repo consistently formatted
- Documentation:
  - Test strategy, architecture, onboarding, test cases, traceability
  - Lightweight ADRs in `docs/adr/` for architectural decisions
- Flaky tests:
  - Explicit policy using `pytest-rerunfailures`
  - Only marked flaky when the external system is unstable; root cause
    is documented and targeted for fixing

---

## Tech stack

- **Language & test runner**
  - Python 3.11+  
  - `pytest`
- **Web UI automation**
  - Selenium WebDriver
  - Chrome / Chromium (headless in CI)
  - Page Object Model pattern
- **API testing**
  - Postman collections
  - Newman CLI (`cli`, `html`, `junit` reporters)
- **Performance testing**
  - Grafana k6 (local CLI and GitHub Action)
- **CI/CD**
  - GitHub Actions (`.github/workflows/ci.yml`)
- **Support tooling**
  - `python-dotenv` for `.env` handling
  - `pytest-xdist`, `pytest-timeout`, `pytest-rerunfailures`

---

## Repository structure

Reflecting what you see in the IDE screenshots:

```text
.github/
  workflows/
    ci.yml                   # GitHub Actions pipeline (lint, UI, API, perf)

autotests/
  README_test_azercell_login.md
  test_azercell_login_page.py   # Main Azercell UI flows (smoke + regression)
  test_smoke.py                 # Minimal smoke test (home → login)

docs/
  adr/
    0001-use-pytest-selenium-pom.md
    0002-ci-gating-smoke-on-pr.md
  architecture.md
  onboarding_guide_for_new_qa.md
  test_cases_azercell_login.md
  test_strategy.md
  traceability_matrix.md        # Test cases → automated tests

pages/
  azercell_login_page.py        # Azercell login Page Object
  base_page.py                  # Shared base Page Object (click, open, windows)
  login_page.py                 # Generic placeholder LoginPage
  __init__.py

postman/
  data/
  environments/
    restful-booker.postman_environment.json
  collections/
    restful-booker.postman_collection.json
  newman/
    run-restful-booker.sh
  README.md

performance/
  restful-booker-smoke.js       # k6 API smoke test

reports/                        # Created at runtime (.gitkeep only)
  downloads/
  screenshots/

utils/
  phone.py                      # normalize_phone_number() helper

conftest.py                     # pytest fixtures, WebDriver, screenshots on fail
pytest.ini                      # markers, default pytest config
requirements.txt                # Python dependencies
.pre-commit-config.yaml         # black + ruff hooks
.gitignore
LICENSE
README.md                       # This file
```

---

## How to run the tests locally

### 1. Prerequisites

- Python 3.11+
- Node.js 18+ (for Newman)
- Google Chrome / Chromium installed

Clone the repo and create a virtual environment:

```bash
git clone https://github.com/<your-username>/<this-repo>.git
cd <this-repo>

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Optional (for API tests):

```bash
npm install -g newman newman-reporter-html newman-reporter-junitfull
```

---

### 2. UI tests (Selenium + pytest)

Basic environment configuration:

```bash
export TEST_ENV="local"
export BASE_URL="https://www.azercell.com/az"
export HEADLESS="1"              # use "0" to see the browser
export WAIT_TIMEOUT="15"
export PAGE_LOAD_TIMEOUT="45"
```

The Azercell login tests can use a real phone number. For safety, the
placeholder `5XXXXXXXXX` is treated as “no real number” and deeper flows
are automatically skipped.

```bash
# Optional – only if you have a real test number
export AZERCELL_PHONE="5XXXXXXXXX"  # format 5XXXXXXXXX, no leading 0
```

Run the **smoke suite** (same idea as PR checks):

```bash
pytest autotests -m smoke -v
```

Run **smoke + regression** (broader coverage):

```bash
pytest autotests -m "smoke or regression" -v
```

On failure, screenshots and page source are stored under:

```text
reports/screenshots/<test_nodeid>_<timestamp>.png
reports/screenshots/<test_nodeid>_<timestamp>.html
```

---

### 3. API tests (Postman + Newman)

```bash
newman run postman/collections/restful-booker.postman_collection.json \
  -e postman/environments/restful-booker.postman_environment.json \
  --reporters cli,junit,html \
  --reporter-junit-export reports/api/postman-junit.xml \
  --reporter-html-export reports/api/postman-results.html
```

These tests cover basic happy paths and negative flows of the
Restful Booker demo API.

---

### 4. Performance smoke (k6)

```bash
export BASE_URL="https://restful-booker.herokuapp.com"
k6 run performance/restful-booker-smoke.js
```

This is a small load test that exercises `/ping` with thresholds on
latency and error rate, meant to show how performance checks can be
integrated into CI rather than to stress the system.

---

## Continuous Integration (GitHub Actions)

Workflow: `.github/workflows/ci.yml`

- Triggers:
  - `push` to `main`
  - `pull_request` targeting `main`
  - `workflow_dispatch` (manual)
  - Nightly `schedule` (`0 0 * * *`)

Jobs:

1. **`lint`**
   - Installs `ruff` and `black`.
   - Runs:
     - `ruff check pages autotests`
     - `black --check pages autotests`

2. **`ui-tests`**
   - Needs `lint`.
   - Installs Chrome on Ubuntu runner.
   - Sets:
     - `BASE_URL=https://www.azercell.com/en`
     - `HEADLESS=1`
   - Injects phone via `PHONE_NUMBER=${{ secrets.AZERCELL_PHONE_NUMBER }}`
     when configured.
   - Runs:
     - On push/PR: `pytest autotests -m "smoke" -v`
     - On nightly schedule: `pytest autotests -m "smoke or regression" -v`
   - Uploads:
     - `reports/ui/ui-junit.xml`
     - Screenshots and page source files.

3. **`api-tests`**
   - Needs `lint`.
   - Sets up Node and Newman.
   - Ensures a Restful Booker environment JSON exists.
   - Runs the Postman collection and uploads:
     - `reports/api/postman-junit.xml`
     - `reports/api/postman-results.html`.

4. **`perf-smoke`**
   - Needs `api-tests`.
   - Runs only on schedule or manual dispatch.
   - Uses official k6 GitHub Actions to execute
     `performance/restful-booker-smoke.js`.

This pipeline shows how I typically gate changes with fast checks on
every PR and push, plus broader regression and performance checks on a
schedule.

---

## Real‑world context (NDA)

In production environments I have:

- Worked with mobile (iOS/Android) automation on BrowserStack
- Built BI / analytics data checks with SQL and API orchestration
- Integrated with TestRail, Jira and release processes
- Owned regression planning and CI gating strategies

Those repos are private, but this project mirrors my approach:
structured automation, strong documentation, and CI as the default way
to run tests.

---

## Contact

- Email: `guseingasimov002@gmail.com`
- LinkedIn: https://www.linkedin.com/in/huseyn-gasimov-
- Location: Baku, Azerbaijan
