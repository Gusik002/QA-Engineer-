# ADR 0002 — CI gating: smoke on PR, regression nightly

Date: 2025-11-24  
Status: Accepted

## Context

Full UI suites are slower and more brittle. For hiring and demo purposes I
want fast feedback on PRs and a realistic pattern for real projects.

## Decision

- On every **pull request**: run lint + smoke UI + smoke API.
- On every **push to main**: run full smoke + standard API collection.
- **Nightly**: run broader regression (UI + API where available).

## Consequences

- PR feedback remains fast and stable.
- Regression issues are still caught by nightly or on-demand full runs.
- CI config uses separate jobs with dependencies and artifacts.

This is the same pattern I prefer in production teams.