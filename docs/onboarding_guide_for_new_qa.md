# QA Onboarding Guide – Azercell UI & Restful Booker API

This document explains how a new QA engineer should get productive with
this repository. It is intentionally written as if this were a small
real project.

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
   pip install -r requirements.txt
   npm install -g newman
   ```

3. **Configure environment variables**

   Minimal setup for UI tests:

   ```bash
   export TEST_ENV="local"
   export BASE_URL="https://www.azercell.com/en"
   export HEADLESS="0"          # set to 1 for headless
   export WAIT_TIMEOUT="15"
   export PAGE_LOAD_TIMEOUT="45"
   ```

   If you have a test phone number:

   ```bash
   export PHONE_NUMBER="5XXXXXXXXX"
   ```

4. **Quick health check**

   ```bash
   pytest autotests/test_smoke.py -m smoke -q
   ```

   You should see one passing smoke test.

---

## 3. How to run suites

### 3.1 UI tests

- **Smoke only (fast, for PRs)**

  ```bash
  pytest autotests -m smoke
  ```

- **Smoke + regression (slower, for nightly or local full check)**

  ```bash
  pytest autotests -m "smoke or regression"
  ```

- **Marking and handling flaky tests**

  Use `@pytest.mark.flaky(reruns=2, reruns_delay=1)` only for tests that
  are unstable due to third‑party or environment issues. Whenever you
  add a flaky marker, add a short comment explaining *why*.

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

GitHub Actions runs on:

- Every push / pull request to `main`
- Nightly at 00:00 UTC
- Manual `workflow_dispatch`

Jobs:

1. `lint` – must be green; treats `ruff` and `black` as a quality gate.
2. `ui-tests`
   - Push/PR: `-m "smoke"` only.
   - Nightly: `-m "smoke or regression"`.
   - Uploads JUnit + screenshots.
3. `api-tests`
   - Runs Restful Booker Postman collection via Newman.
4. `perf-smoke`
   - Runs small k6 test on schedule/manual to catch performance drift.

When a job fails:

- Open the build, download artifacts.
- For UI failures, start with the JUnit XML and matching screenshot /
  HTML page source.
- For API failures, inspect the Newman HTML report.

Document anything non‑obvious in the relevant test case or in the
`docs/` folder.

---

## 5. Adding a new UI test

1. **Add selectors and actions** to a page object in `pages/` (or create
   a new one inheriting from `BasePage`).
2. **Add a test** in `autotests/` following existing style:

   - Small, focused.
   - Use fixtures (`browser`, `wait`, `login_page`).
   - Mark with one of: `@pytest.mark.smoke`,
     `@pytest.mark.regression`, `@pytest.mark.slow`.
   - If it maps to a test case, use `@pytest.mark.testcase("TC‑ID")`.

3. **Run locally** with the right markers.
4. **Update documentation** (test cases file or traceability matrix) if
   you’re covering a new risk or requirement.

---

## 6. Adding a new API test

1. Extend the Postman collection under `postman/collections/`.
2. Decide which folder it belongs to:
   - `Health`, `Auth`, `Booking_Happy Path`, or `Booking_Negative`.
3. Add clear `pm.test` assertions:
   - Status code.
   - Response time threshold where relevant.
   - Business‑level checks on the JSON body.
4. Re‑run Newman locally, then push and verify in CI.

---

## 7. Coding standards

- Python code must pass `ruff` and `black` (enforced in CI).
- Keep tests readable:
  - One logical scenario per test.
  - Clear asserts with custom messages.
- Prefer explicit waits over `time.sleep`, except where you are modelling
  a real user delay.

---

## 8. When in doubt

If you are unsure whether a test should be smoke or regression:

- **Smoke** if:
  - It verifies a single critical happy path.
  - It’s fast and stable.
- **Regression** if:
  - It exercises error handling or edge cases.
  - It needs more setup/data and might be slower.

If you feel you need a flaky marker, raise it in a code review and
document the reason in the test docstring.