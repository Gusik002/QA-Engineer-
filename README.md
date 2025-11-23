# QA Automation Portfolio – Huseyn Gasimov

This repository showcases how I approach quality engineering across web UI,
APIs, and CI/CD. It uses public systems (the Azercell login page and the
Restful Booker API) to demonstrate my testing style without exposing any
NDA‑protected work.

The focus is on small, reliable suites wired into CI, clear reporting, and
practical tooling rather than huge “test everything” packs.

---

## What this repository demonstrates

- **Cross‑layer testing:** web UI (Selenium/pytest) and API checks
  (Postman/Newman), plus basic reporting.
- **CI‑first mindset:** tests run on every push and pull request in
  GitHub Actions; results are published as JUnit/HTML artifacts.
- **Risk‑based design:** focused smoke coverage for critical user paths,
  including positive and negative scenarios.
- **Maintainable automation:** Page Object Model, shared fixtures, and
  environment‑aware configuration.

---

## Tech stack

- **Language & test runner**
  - Python 3.11, `pytest`
- **Web UI automation**
  - Selenium WebDriver
  - Page Object Model (POM)
- **API testing**
  - Postman collections
  - Newman CLI + HTML/JUnit reporters
- **CI/CD**
  - GitHub Actions (`.github/workflows/ci.yml`)
- **Other tooling**
  - Chrome/Chromium (headless in CI)
  - JUnit XML + HTML reports (uploaded as build artifacts)

Real production work (mobile, BI, broader API suites) is under NDA, but
the structure here mirrors how I work on those projects.

---

## Repository structure

```text
.github/
  workflows/
    ci.yml              # GitHub Actions pipeline

autotests/              # pytest UI tests (Selenium)
  test_azercell_login_page.py
  test_smoke.py         # Example smoke/regression grouping

pages/                  # Page Object Model classes
  azercell_login_page.py
  login_page.py
  __init__.py

postman/
  collections/          # RESTful Booker Postman collection
  environments/         # Local/CI environments
  newman/               # Example Newman configs (if needed)
  reports/              # Local Newman report outputs (git‑ignored)

reports/
  screenshots/          # Example screenshots from UI runs
  README.md             # Notes about local reports (optional)

conftest.py             # Shared pytest fixtures (driver, waits, etc.)
pytest.ini              # Pytest configuration and markers
requirements.txt        # Python dependencies
README.md               # This file
```

Folder names may evolve, but the idea is to keep UI tests, page objects,
and API collections clearly separated.

---

## Running tests locally

### 1. Prerequisites

- Python **3.11+**
- Node.js **18+** with `npm`
- Google Chrome or Chromium installed locally

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/<your-username>/<this-repo>.git
cd <this-repo>

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

Install Python dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Install Newman globally (for API tests):

```bash
npm install -g newman newman-reporter-html newman-reporter-junitfull
```

---

### 2. Run UI tests (Selenium + pytest)

If your tests require a phone number (for OTP flows), export it as an
environment variable:

```bash
export PHONE_NUMBER="YOUR_TEST_PHONE_NUMBER"
```

Then run the UI suite:

```bash
pytest autotests -q
```

To generate a local JUnit report:

```bash
pytest autotests -q --junitxml=reports/ui-junit.xml
```

By default, tests will run using the browser defined in your fixtures. In
CI a headless Chromium/Chrome is used.

---

### 3. Run API tests (Postman + Newman)

The main collection is `postman/collections/restful-booker.postman_collection.json`.

If the environment file is missing, CI will generate one automatically,
but locally you can use or adjust:

```bash
postman/environments/restful-booker.postman_environment.json
```

Run the collection via Newman:

```bash
newman run postman/collections/restful-booker.postman_collection.json \
  -e postman/environments/restful-booker.postman_environment.json \
  --reporters cli,junit,html \
  --reporter-junit-export reports/postman-junit.xml \
  --reporter-html-export reports/postman-results.html
```

This produces both machine‑readable (JUnit XML) and human‑readable
(HTML) reports.

---

## Continuous Integration (GitHub Actions)

The workflow file lives in `.github/workflows/ci.yml`.

It currently runs on:

- Every push to `main`
- Every pull request targeting `main`
- Manual runs via the **Run workflow** button
- A scheduled nightly run (see `cron` in the workflow)

### CI jobs

1. **`lint`**
   - Installs `ruff` and `black`.
   - Runs static checks over the Python test code (`pages/`, `autotests/`).

2. **`ui-tests`**
   - Depends on `lint`.
   - Sets up Python and project dependencies.
   - Installs Chromium/Chrome in headless mode.
   - Executes the Selenium UI tests with `pytest`.
   - Publishes JUnit XML reports as a `ui-test-reports` artifact.

3. **`api-tests`**
   - Depends on `lint`.
   - Sets up Node.js and installs Newman + reporters.
   - Ensures a Postman environment file exists (creates a default CI one
     if needed).
   - Runs the Restful Booker collection with Newman.
   - Publishes JUnit XML and HTML reports as an `api-test-reports`
     artifact.

This mirrors how I typically wire smoke and API suites into CI for early,
visible feedback on each change.

---

## How this reflects my testing approach

- Start from **user journeys** and key backend flows, then design lean
  smoke and regression packs.
- Automate **critical paths only**, keeping them stable and fast enough
  to run on every build.
- Keep **defects reproducible** with logs, screenshots and environment
  details so developers can act quickly.
- Use **CI as the single source of truth** for quality gates (smoke on
  every PR, fuller coverage on nightly runs).

---
## Docs & test cases

See `docs/test_strategy.md` for the repo testing strategy and CI
gating. Example test cases for the Azercell login flow are in:
`docs/test_cases_azercell_login.md`.

How to run (quick)
- Install deps: `pip install -r requirements.txt`
- Run UI smoke: `pytest autotests/test_smoke.py -q`
- Run all Postman: `newman run postman/collections/... -e postman/environments/...`
CI uploads JUnit/HTML reports to actions artifacts.
## Real‑world context (NDA)

My production experience includes:

- Mobile (iOS/Android) testing and automation with Appium on BrowserStack
- BI and web analytics platforms with SQL‑based data validation
- Release gating, regression planning, and TestRail/Jira workflows

Those projects are under NDA, so this repository uses public targets, but
follows the same structure and practices I apply at work.

---

## Contact

- **Email:** guseingasimov002@gmail.com  
- **LinkedIn:** https://www.linkedin.com/in/huseyn-gasimov  
- **Location:** Baku, Azerbaijan
