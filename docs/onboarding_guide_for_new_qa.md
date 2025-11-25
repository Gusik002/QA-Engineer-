# QA Onboarding Guide – Azercell UI & Restful Booker API

This document explains how a new QA engineer can get productive with
this repository. It is written as if this were a small real project.

---

## 1. Goals of this project

- Demonstrate how we structure UI, API, and performance tests.
- Show how tests plug into CI and how failures are triaged.
- Provide examples of documentation, traceability, and collaboration
  practices.

You should be able to:

- Run a smoke suite locally and in CI.
- Add a new UI or API test following the existing patterns.
- Understand how tests map to requirements and risks.

---

## 2. Local setup

1. **Clone and create virtualenv**

   ```bash
   git clone https://github.com/<your-username>/<this-repo>.git
   cd <this-repo>

   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt

   # Optional: for local Newman runs
   npm install -g newman
   ```

3. **Configure environment variables**

   Minimal setup for UI tests:

   ```bash
   export TEST_ENV="local"
   export BASE_URL="https://www.azercell.com/az"   # or /en if preferred
   export HEADLESS="0"          # set to "1" for headless
   export WAIT_TIMEOUT="15"
   export PAGE_LOAD_TIMEOUT="45"
   ```

   If you have access to a test phone number for Azercell login flows:

   ```bash
   # Recommended format: 5XXXXXXXXX (no leading 0 or +994)
   export AZERCELL_PHONE="5XXXXXXXXX"
   ```

   You can also use a `.env` file in the project root, which is
   automatically loaded via `python-dotenv`.

4. **Quick health check**

   Run the basic UI smoke tests:

   ```bash
   pytest autotests -m smoke -v
   ```

   You should see the Azercell home/login tests passing. Tests that
   require a real phone number will be skipped if you only use the
   placeholder `5XXXXXXXXX`.

---

## 3. How to run suites

### 3.1 UI tests (pytest + Selenium)

- **Smoke only (fast, for PRs)**

  ```bash
  pytest autotests -m smoke -v
  ```

- **Smoke + regression (slower, for nightly or local full check)**

  ```bash
  pytest autotests -m "smoke or regression" -v
  ```

- **Run a specific test file**

  ```bash
  pytest autotests/test_azercell_login_page.py -v
  ```

- **Run a single test**

  ```bash
  pytest autotests/test_azercell_login_page.py::test_complete_flow_to_otp_page -v
  ```

- **Marking and handling flaky tests**

  Use `@pytest.mark.flaky(reruns=2, reruns_delay=1)` only for tests that
  are unstable due to third‑party or environment issues (e.g. external
  site slowness). Whenever you add a flaky marker, add a short comment
  explaining *why*.

### 3.2 API tests (Postman/Newman)

```bash
newman run postman/collections/restful-booker.postman_collection.json \
  -e postman/environments/restful-booker.postman_environment.json \
  --reporters cli,junit,html \
  --reporter-junit-export reports/api/postman-junit.xml \
  --reporter-html-export reports/api/postman-results.html
```

### 3.3 Performance smoke (k6)

```bash
export BASE_URL="https://restful-booker.herokuapp.com"
k6 run performance/restful-booker-smoke.js
```

---

## 4. CI expectations

GitHub Actions workflow: **QA Portfolio CI**

Runs on:

- Every push / pull request to `main`
- Nightly at 00:00 (cron)
- Manual `workflow_dispatch`

Jobs:

1. **`lint`**
   - Runs `ruff` and `black --check` on `pages` and `autotests`.
   - Must be green; enforces style and basic static checks.

2. **`ui-tests`**
   - Installs Google Chrome on the runner.
   - Push/PR: runs pytest with `-m "smoke"`.
   - Nightly schedule: runs `-m "smoke or regression"`.
   - Uses a phone number injected via GitHub secret
     (`AZERCELL_PHONE_NUMBER`) when configured.
   - Uploads JUnit XML, screenshots and page source as artifacts.

3. **`api-tests`**
   - Executes the Restful Booker Postman collection via Newman.
   - Uploads JUnit XML and HTML reports.

4. **`perf-smoke`**
   - Runs a small k6 performance script on schedule or manual trigger.
   - Not required for every PR; focuses on catching obvious performance
     regressions over time.

When a job fails:

- Open the failing workflow run.
- Download artifacts:
  - For UI failures: start with the JUnit XML and the screenshot/HTML
    for the failing test.
  - For API failures: open the Newman HTML report.
- Update test docstrings or notes in `docs/` when you discover
  non-obvious behaviours.

---

## 5. Adding a new UI test

1. **Update or create a Page Object** in `pages/`:
   - Inherit from `BasePage`.
   - Add clear methods (`open_*`, `click_*`, `enter_*`, etc.).
   - Keep locators and Selenium calls inside the Page Object.

2. **Add a test** in `autotests/` following existing style:
   - Small, focused scenario.
   - Uses fixtures like `browser`, `wait`, or a dedicated fixture such
     as `login_page`.
   - Marked with one of: `@pytest.mark.smoke`,
     `@pytest.mark.regression`, `@pytest.mark.slow`.
   - Optionally `@pytest.mark.testcase("AZ-LG-0XX")` to link to a test
     case ID.

3. **Run locally** with relevant markers.

4. **Update documentation**:
   - Add or adjust entries in `docs/test_cases_*.md`.
   - Ensure `docs/traceability_*.md` maps the new test to its case ID.

---

## 6. Adding a new API test

1. Extend the Postman collection under `postman/collections/`:
   - Group requests into logical folders (`Auth`, `Booking_Happy`,
     `Booking_Negative`, etc.).

2. Use clear `pm.test` assertions:
   - Status code.
   - Response time thresholds where relevant.
   - Business-level checks on JSON structure and values.

3. Run Newman locally and verify:

   ```bash
   newman run postman/collections/restful-booker.postman_collection.json \
     -e postman/environments/restful-booker.postman_environment.json
   ```

4. Push your changes and verify the `api-tests` job in CI.

---

## 7. Coding standards

- Python code must pass `ruff` and `black` (CI enforces this).
- Keep test functions readable:
  - One logical scenario per test.
  - Explicit assertions with helpful messages.
- Prefer explicit waits (`WebDriverWait`) over `time.sleep`, except
  for small, intentional pauses (e.g. modelling a brief user delay).
- Keep Page Objects cohesive: no business logic in tests, no assertions
  in Page Objects unless they’re simple sanity checks.

---

## 8. When in doubt

If you’re unsure whether a test should be smoke or regression:

- **Smoke** if:
  - It verifies a single critical happy path.
  - It’s fast and very stable.
- **Regression** if:
  - It exercises edge cases or error handling.
  - It requires more setup or is inherently slower.

If you feel a test needs a flaky/xfail marker, raise it in code review
and capture the reason in the test docstring and/or `docs/` notes.