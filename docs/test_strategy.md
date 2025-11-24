# Test strategy — QA Portfolio (Huseyn Gasimov)

Purpose
-------
This document explains the testing approach illustrated by this
repository. It demonstrates how I design small, reliable suites that
protect releases and provide fast feedback to developers.

Scope
-----
- Public examples: Azercell login UI and Restful Booker API
- Demonstrates cross-layer testing: UI (Selenium/POM), API (Postman/
  Newman), and data checks.
- Focus on smoke (fast) and regression (thorough) packs rather than
  full exhaustive automation.

Test pyramid & priorities
-------------------------
- Unit / Component (not included here) — developer responsibility.
- API / Integration — high value, medium speed. Cover auth, critical
  workflows and boundary/error cases.
- UI / End-to-end — small, focused smoke checks for critical journeys.

Risk-based selection
--------------------
- Identify user journeys that must be protected on every PR (smoke).
- Run larger regression/nightly suites for broader coverage.
- Prioritise flaky-prone or brittle checks for manual review or
  stabilization before adding to CI.

CI gating & cadence
-------------------
- Pull Request: run smoke UI + API checks for quick feedback.
- Push to main: run full smoke + Newman API with JUnit/HTML reports.
- Nightly: run broader API/regression pack and upload artifacts.

Environments & test data
------------------------
- Use environment files for Postman (stored in repo for public
  examples; secrets used for private creds).
- Isolate test data — create / tear down entities where possible.
- Seed stable test accounts for deterministic results.

Flaky test policy
-----------------
- Short-term: mark flaky tests with @pytest.mark.flaky/xfail and notify
  owner in PR description.
- Long-term: fix the root cause (timing, locator robustness,
  environment issues) before adding to smoke.

Reporting & observability
-------------------------
- Upload JUnit XML + HTML reports as CI artifacts.
- Attach screenshots and minimal logs for UI failures.
- Track basic metrics (run time, failure rates, flaky tests) over time.

Quality metrics
---------------
Suggested measurable KPIs:
- PR feedback time (time from push to first failing/successful CI).
- Flaky rate (tests failing intermittently across runs).
- Regression cycle time (full suite runtime).
- Defect leakage to production (target near 0 for critical flows).

Adding new tests (guidelines)
-----------------------------
- Prefer API tests before UI for business logic.
- Add small, focused UI smoke tests only for high-risk flows.
- Follow Page Object Model for UI code; keep locators in one file.
- Add a short test case in `docs/test_cases_*.md` when adding
  non-trivial checks.

Notes
-----
This repository intentionally demonstrates structure and approach
rather than exhaustive coverage. For production projects I also include:
- Test data factories
- Canary health checks
- Integration with test management (TestRail) and defect trackers
