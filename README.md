# QA Portfolio — Huseyn Gasimov

I am a QA Engineer with a little over two years of hands-on experience across
BI dashboards, web applications, and mobile apps (iOS/Android). I focus on
data correctness, fast developer feedback, and clear, reproducible defects
rather than just executing test cases.

## What I work on

- API and backend testing with Postman/Newman and SQL-based data checks
- Mobile testing and debugging with Android Studio, Xcode, BrowserStack,
  Charles, Proxyman
- Release gating and regression planning for BI, web and mobile releases
- Lightweight automation (Appium, pytest/Playwright) wired into CI for
  critical-path stability

## Recent project highlights

### Employment platform (event-driven microservices, mobile apps) — QA Engineer

- Defined an iOS/Android coverage matrix (5 physical devices + BrowserStack)
  targeting main user segments and reduced “untested device” escapes.
- Ran a focused 40-case smoke suite for each release candidate via TestFlight
  and Google Play Internal Testing, improving release confidence and
  shortening go/no-go decisions.
- Reproduced and diagnosed crashes using Android Studio emulator, Xcode
  simulator, device logs and network traces; provided clear repro steps,
  logs and recordings to developers.
- Verified offline/sync and degraded-network behaviour with Charles Proxy
  and Proxyman and uncovered data-consistency gaps between app and backend.
- Built a lightweight Appium smoke suite (~20 critical paths) on BrowserStack
  and integrated it into CI (per-PR + nightly), reducing escaped mobile
  regressions by ~20% and surfacing failures within ~15 minutes.
- Added a focused Postman pack for mobile-critical APIs (auth, profile,
  sync) with environment-aware scripts and CI reporting; blocked 10+ API
  defects before RC builds and cut triage time by ~25%.

### BI & web analytics platform — QA Engineer

- Built and maintained 120+ Postman API tests with reusable environments
  and scripts; blocked 30+ API defects before staging.
- Integrated Newman into CI for nightly multi-environment runs with
  JUnit/HTML reporting, shortening feedback loops.
- Led regression for several BI/web modules; trimmed the suite by 26%
  while preserving ~95% functional coverage and cutting cycle time by ~35%.
- Authored 300+ TestRail cases and introduced tag-based filters
  (smoke/regression), improving test selection speed by ~40%.
- Wrote SQL reconciliation checks to validate dashboards against source
  tables and surfaced data integrity issues early.
- Standardised Jira defect templates and attachments (device/profile,
  steps, logs, screenshots/video), improving defect quality and reducing
  reopen/triage time by ~25%.
- Collaborated with product and engineering on acceptance criteria and
  release gating, increasing first-pass acceptance in sprints.

## Skills and tools

- **APIs & data:** Postman, Newman (CI), Swagger/OpenAPI, REST, SQL,
  BI dashboard reconciliation
- **Mobile & debugging:** Android Studio, Xcode, Charles Proxy, Proxyman,
  BrowserStack, TestFlight, Google Play Internal Testing
- **Test management:** TestRail (tagged suites, coverage), Jira
  (workflows, templates), Chrome DevTools
- **Automation & CI:** Appium (smoke), Python (scripting), learning Java,
  Playwright/pytest basics, CI test reporting (JUnit/HTML)
- **Methods:** Agile/Scrum/Kanban; SDLC/STLC
- **Languages:** English (C2, IELTS 8), Japanese (JLPT N3), Azerbaijani
  (native), Russian (native)

## How I like to test

- Start from user journeys and data flows, then design lean smoke and
  regression suites that reflect real risk.
- Automate the critical paths that must stay green on every build; keep
  those checks fast, stable and visible in CI.
- Keep defects small, clear and reproducible, with logs, screenshots,
  videos and environment details so engineers can fix issues quickly.
- Use CI to catch regressions early, protect release quality, and make
  go/no-go decisions based on data.

## About this portfolio

This repository demonstrates how I approach QA in practice and will
contain:

- API test collections (Postman/Newman) with environment-aware scripts
- Example SQL checks for BI/dashboard validation
- Lightweight Python/pytest and Appium examples for critical-path tests
- A simple CI workflow that runs checks on every push and pull request

The emphasis is on small, focused suites wired into CI, clear reporting,
and practical tooling rather than long lists.

## Education

- Master’s Degree in Renewable Energy (MSc) — Warwick University,
  United Kingdom (2023–2025)  
- Bachelor’s Degree in Oil and Gas Engineering — Azerbaijan State Oil and
  Industry University (2019–2023)

## Contact

- Email: guseingasimov002@gmail.com  
- LinkedIn: https://www.linkedin.com/in/huseyn-gasimov  
- Phone: +994 55 207 08 20  
- Location: Baku, Azerbaijan
