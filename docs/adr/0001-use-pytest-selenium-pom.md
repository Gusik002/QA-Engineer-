# ADR 0001 — Use pytest + Selenium + POM

Date: 2025-11-24  
Status: Accepted

## Context

Need a simple but realistic stack to demonstrate UI automation skills on a
public site (Azercell) that:

- is Python-based,
- integrates easily with GitHub Actions,
- supports Page Object Model,
- is understandable for most QA/Dev teams.

## Decision

Use:

- `pytest` as test runner,
- `selenium` for browser automation,
- `webdriver-manager` for local/CI driver downloads,
- Page Object Model (`pages/*`) for maintainability.

## Consequences

- Clear separation between tests and UI details.
- Requires Chrome/Chromium/driver set up in CI (done via
  `browser-actions/setup-chrome`).
- Easier for reviewers to understand vs. heavy frameworks.

Alternatives (Playwright, Cypress, Robot) are valid, but Selenium is still
most universal in mixed tech teams, especially for Python.