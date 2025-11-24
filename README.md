# QA Automation Portfolio – Huseyn Gasimov

For recruiters – start here
---------------------------

1. **High-level overview**  
   - `docs/architecture.md`  
   - `docs/test_strategy.md`

2. **Traceability (requirements → tests)**  
   - `docs/traceability_matrix.md`

3. **UI automation example (Selenium + pytest)**  
   - Tests: `autotests/test_azercell_login_page.py`,
     `autotests/test_smoke.py`  
   - Page objects: `pages/azercell_login_page.py`, `pages/base_page.py`

4. **API tests (Postman + Newman)**  
   - Collection: `postman/collections/restful-booker.postman_collection.json`  
   - CI job: `.github/workflows/ci.yml` → `api-tests`

5. **Performance smoke (k6)**  
   - Script: `performance/restful-booker-smoke.js`  
   - CI job: `.github/workflows/ci.yml` → `perf-smoke`

6. **Process / leadership**  
   - Onboarding guide: `docs/onboarding_guide_for_new_qa.md`  
   - Test cases: `docs/test_cases_azercell_login.md`

---

## Overview

This repository showcases how I approach quality engineering across web
UI, APIs, and CI/CD. It uses public systems (the Azercell login page and
the Restful Booker API) to demonstrate my testing style without exposing
any NDA‑protected work.

The focus is on **small, reliable suites wired into CI**, clear
reporting, and practical tooling rather than huge “test everything”
packs.

---

## What this repository demonstrates

- **Cross‑layer testing**  
  Web UI (Selenium/pytest), API checks (Postman/Newman), and a small k6
  performance smoke.

- **CI‑first mindset**  
  Tests run on every push and pull request in GitHub Actions; nightly
  runs execute a broader regression pack; results are published as
  JUnit/HTML artifacts.

- **Risk‑based test design**  
  Focused smoke coverage for critical user paths, including both
  positive and negative scenarios.

- **Maintainable automation**  
  Page Object Model, shared pytest fixtures, and environment‑aware
  configuration driven by `BASE_URL`, `HEADLESS`, timeouts, and
  environment labels.

- **Engineering discipline**  
  Linting (`ruff`, `black`), pre‑commit hooks, readable docs, and
  explicit handling of flaky tests.

---

## Tech stack

- **Language & test runner**
  - Python 3.11, `pytest`
- **Web UI automation**
  - Selenium WebDriver
  - Page Object Model (POM)
- **API testing**
  - Postman collections
  - Newman CLI with HTML/JUnit reporters
- **Performance testing**
  - Grafana k6 (CLI + GitHub Action)
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
    ci.yml                    # GitHub Actions pipeline

autotests/                    # pytest UI tests (Selenium)
  test_azercell_login_page.py
  test_smoke.py               # Example smoke/regression grouping

pages/                        # Page Object Model classes
  base_page.py
  azercell_login_page.py
  login_page.py
  __init__.py

postman/
  collections/                # Restful Booker Postman collection
    restful-booker.postman_collection.json
  environments/               # Local/CI environments
  newman/                     # Example Newman shell wrapper
  README.md

performance/
  restful-booker-smoke.js     # k6 performance smoke script

reports/
  (created at runtime)
  ui/                         # UI JUnit + screenshots (CI)
  api/                        # Newman JUnit + HTML (CI)

docs/
  architecture.md
  test_strategy.md
  traceability_matrix.md
  test_cases_azercell_login.md
  onboarding_guide_for_new_qa.md

conftest.py                   # Shared pytest fixtures (driver, waits, artifacts)
pytest.ini                    # Pytest configuration and markers
requirements.txt              # Python dependencies
.pre-commit-config.yaml       # Lint/format hooks
README.md                     # This file
```

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

Optional: install k6 locally for performance smoke:

```bash
# Example for macOS
brew install k6
```

---

### 2. Run UI tests (Selenium + pytest)

Export optional environment variables:

```bash
export TEST_ENV="local"
export BASE_URL="https://www.azercell.com/en"
export HEADLESS="0"               # use 1 for headless
export WAIT_TIMEOUT="15"
export PAGE_LOAD_TIMEOUT="45"
export PHONE_NUMBER="YOUR_TEST_PHONE_NUMBER"  # optional
```

**Smoke suite (fast, for local checks / PR parity):**

```bash
pytest autotests -m smoke
```

**Smoke + regression (broader, similar to nightly CI):**

```bash
pytest autotests -m "smoke or regression"
```

To generate a local JUnit report:

```bash
pytest autotests -m "smoke or regression" \
  --junitxml=reports/ui/ui-junit.xml
```

Screenshots and page source from failing tests are stored under
`reports/ui/screenshots/`.

---

### 3. Run API tests (Postman + Newman)

Main collection:

```text
postman/collections/restful-booker.postman_collection.json
```

Environment (can be adjusted locally):

```text
postman/environments/restful-booker.postman_environment.json
```

Run via Newman:

```bash
newman run postman/collections/restful-booker.postman_collection.json \
  -e postman/environments/restful-booker.postman_environment.json \
  --reporters cli,junit,html \
  --reporter-junit-export reports/api/postman-junit.xml \
  --reporter-html-export reports/api/postman-results.html
```

---

### 4. Run performance smoke (k6)

```bash
export BASE_URL="https://restful-booker.herokuapp.com"
k6 run performance/restful-booker-smoke.js
```

This executes a short load test against `/ping` with simple thresholds on
latency and error rate.

---

## Continuous Integration (GitHub Actions)

The workflow file lives in `.github/workflows/ci.yml`.

It runs on:

- Every push to `main`
- Every pull request targeting `main`
- Manual runs via the **Run workflow** button
- A scheduled nightly run at `00:00` UTC

### CI jobs

1. **`lint`**
   - Installs `ruff` and `black`.
   - Runs static checks over the Python automation code
     (`pages/`, `autotests/`).
   - Fails the pipeline if style checks fail (quality gate).

2. **`ui-tests`**
   - Needs `lint`.
   - Installs Python deps + Chrome, configures headless mode for CI.
   - Push / PR: runs only `-m "smoke"` for fast feedback.
   - Nightly schedule: runs `-m "smoke or regression"` for broader
     coverage.
   - Publishes JUnit XML and screenshots/page source under the
     `ui-test-artifacts` artifact.

3. **`api-tests`**
   - Needs `lint`.
   - Sets up Node.js and installs Newman + reporters.
   - Ensures a CI Postman environment JSON exists.
   - Runs the Restful Booker collection with positive and negative
     flows.
   - Publishes JUnit XML and HTML reports as `api-test-artifacts`.

4. **`perf-smoke`**
   - Needs `api-tests`.
   - Runs only on `schedule` or manual `workflow_dispatch`.
   - Uses official `setup-k6-action` and `run-k6-action` to execute
     `performance/restful-booker-smoke.js` against `/ping`.
   - Fails the build if latency or error thresholds are violated.

This setup mirrors how I typically wire smoke, API, and light
performance checks into CI for early, visible feedback.

---

## Flaky tests and reruns

Occasionally a test can be unstable due to external systems
(third‑party services, demo environments). For those cases:

- The project uses `pytest-rerunfailures`.
- Tests may be marked as:

  ```python
  @pytest.mark.flaky(reruns=2, reruns_delay=1)
  ```

- Each flaky test must have:
  - A comment or docstring explaining the reason.
  - A clear plan to remove the flakiness (or move it out of smoke).

This shows that flakiness is **managed**, not ignored.

---

## Docs & test cases

Key documentation:

- `docs/test_strategy.md` – overall testing strategy and CI gating.
- `docs/traceability_matrix.md` – mapping of risks/features to tests.
- `docs/test_cases_azercell_login.md` – example UI test cases.
- `docs/onboarding_guide_for_new_qa.md` – how a new QA joins and works
  with this repo.

---

## Real‑world context (NDA)

My production experience includes:

- Mobile (iOS/Android) testing and automation with Appium on BrowserStack
- BI and web analytics platforms with SQL‑based data validation
- Release gating, regression planning, and TestRail/Jira workflows

Those projects are under NDA, so this repository uses public targets but
follows the same structure and practices I apply at work.

---

## Contact

- **Email:** guseingasimov002@gmail.com  
- **LinkedIn:** https://www.linkedin.com/in/huseyn-gasimov-  
- **Location:** Baku, Azerbaijan