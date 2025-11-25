# Test strategy — QA Portfolio (Huseyn Gasimov)

## Purpose

This document explains the testing approach illustrated by this
repository. It shows how I design small, reliable suites that protect
releases and provide fast feedback to developers.

## Scope

- Public examples:
  - Azercell login UI (Selenium + pytest + Page Objects)
  - Restful Booker API (Postman + Newman)
  - Light API performance smoke (k6)
- Demonstrates cross-layer testing:
  - UI end-to-end flows
  - API/integration checks
- Focus on:
  - Fast **smoke** packs for PRs
  - Deeper **regression** packs on nightly / on demand

## Test pyramid & priorities

- **Unit / Component** (not fully included here)
  - Owned by developers.
  - Cheap, fast checks close to the code.

- **API / Integration**
  - High value, medium speed.
  - Cover auth, booking flows, boundary/error cases.
  - Implemented via Postman + Newman and k6.

- **UI / End-to-end**
  - Thin layer of small, focused smoke checks:
    - Azercell home page and login availability.
    - Core login journey with live or test data where possible.
  - Deeper regression tests gated by data availability and stability.

## Risk-based selection

- Identify user journeys that **must** be protected on every PR:
  - Azercell home → login page reachable.
  - Login page phone input works with valid number.
- Run broader regression / exploratory suites:
  - On nightly schedules.
  - On-demand before bigger releases.
- Treat brittle or very slow scenarios carefully:
  - Start as regression-only.
  - Stabilize before moving into smoke.

## CI gating & cadence

GitHub Actions workflow `QA Portfolio CI` runs on:

- Every push and pull request to `main`
- Nightly at 00:00 (cron)
- Manual dispatch

Jobs:

1. **`lint`**
   - Runs `ruff` and `black --check` against UI test code.
   - Acts as an early gate for code quality and basic issues.

2. **`ui-tests`**
   - Installs Google Chrome via `apt`.
   - Uses pytest markers:
     - Push/PR: `-m "smoke"`
     - Nightly/scheduled: `-m "smoke or regression"`
   - Reads phone number for Azercell flows from CI secrets.
   - Uploads JUnit XML + screenshots + HTML sources.

3. **`api-tests`**
   - Runs Newman with the Restful Booker collection.
   - Produces JUnit XML and HTML reports for debugging.

4. **`perf-smoke`**
   - Runs a small k6 script on schedule or manual trigger.
   - Not required for every PR; focused on long-term performance
     health.

## Environments & test data

- **UI**
  - Uses environment variables to control:
    - `TEST_ENV`, `BASE_URL`, `AZERCELL_LOGIN_URL`
    - Timeouts (`WAIT_TIMEOUT`, `PAGE_LOAD_TIMEOUT`)
    - Browser headless mode (`HEADLESS`).
  - Uses `AZERCELL_PHONE` / `PHONE_NUMBER` for live login tests,
    defaulting to a placeholder that safely skips deep flows.

- **API**
  - Postman environment JSON under `postman/environments/`.
  - Credentials are demo-level (Restful Booker) and may be overridden by
    CI secrets for real systems.

- **Data isolation**
  - Where practical, test data is created/cleaned up via API.
  - For public demos, focus is on idempotent operations and safe data.

## Flaky test policy

- **Short-term:**
  - Mark flaky tests with `@pytest.mark.flaky(...)` or `xfail` where
    instability is due to:
    - External dependencies (3rd party site slowness).
    - Non-deterministic test data.
  - Document the reason in the test docstring and/or PR description.

- **Long-term:**
  - Fix the root cause:
    - Improve locators or waiting strategy.
    - Stabilize test data.
    - Isolate network dependency where possible.
  - A test should not live permanently as “flaky” in the smoke suite.

## Reporting & observability

- **UI**
  - JUnit XML from pytest.
  - Screenshot + HTML capture on failure via
    `pytest_runtest_makereport`.
  - Artifacts uploaded for each CI run.

- **API**
  - Newman JUnit XML for integration with CI.
  - Newman HTML report for human-friendly failure triage.

- **Performance**
  - k6 CLI output and optional result files.

## Quality metrics (suggested)

- **PR feedback time**
  - Time from push to green/red CI.
  - Target: minutes, not hours.

- **Flaky rate**
  - Percentage of tests that fail intermittently across runs.
  - Aim to keep this very low, especially in smoke.

- **Regression cycle time**
  - Runtime of full smoke + regression suites.
  - Measured to avoid suites becoming too slow to be useful.

- **Defect leakage**
  - Issues found after deployment in areas covered by automation.
  - Target near 0 for critical flows.

## Adding new tests (guidelines)

- Prefer **API tests** over UI where business logic can be exercised
  without a browser.
- Add small, focused **UI smoke tests** only for high-risk flows (e.g.
  login, checkout, critical dashboards).
- Follow the Page Object Model:
  - Keep locators and interactions in `pages/`.
  - Keep assertions in test files.
- For non-trivial checks:
  - Add/update a case in `docs/test_cases_*.md`.
  - Link test functions to case IDs via `@pytest.mark.testcase(...)`.

## Notes

This repository intentionally demonstrates structure and approach rather
than exhaustive coverage. In production projects I would also include:

- Test data factories and seeding strategies.
- Health checks / canary tests for production monitoring.
- Integration with test management tools (e.g. TestRail) and defect
  trackers.
- More extensive non-functional tests (security, accessibility, load).