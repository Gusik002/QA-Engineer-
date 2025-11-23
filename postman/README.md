# Postman / Newman — Restful Booker API tests

Purpose
-------
This folder contains an exported Postman collection and environment that demonstrate API testing
skills for a public demo API (Restful Booker). It is safe to share and is intended for portfolio
review by HR/technical interviewers.

What is included
----------------
- collections/restful-booker.postman_collection.json — Collection with folders:
  - Health (Ping)
  - Auth (Create token)
  - Booking_Happy_Path (Create, Get, PUT, PATCH, DELETE)
  - Booking_Negative (missing fields, invalid JSON, invalid token, not-found)
- environments/restful-booker.postman_environment.json — environment with baseUrl, creds,
  and placeholders (token, bookingId).
- newman/run-restful-booker.sh — script to run the collection using Newman and produce reports.
- reports/ — generated test reports (gitignored)

How to import into Postman
--------------------------
1. In Postman, Import → choose `collections/restful-booker.postman_collection.json`.
2. Import environment: Environments → Import → `environments/restful-booker.postman_environment.json`.
3. Select environment at top-right (Restful Booker - public).

How to run locally (Newman)
---------------------------
Prerequisites:
- Node.js (12+)
- npm

Install newman and reporters:
```bash
npm install -g newman newman-reporter-html newman-reporter-junitfull
```

Run:
```bash
postman/newman/run-restful-booker.sh
# or use newman directly:
newman run postman/collections/restful-booker.postman_collection.json \
  -e postman/environments/restful-booker.postman_collection.json \
  --reporters cli,junit,html \
  --reporter-junit-export postman/reports/newman-results.xml \
  --reporter-html-export postman/reports/newman-results.html
```

CI (GitHub Actions)
-------------------
See `.github/workflows/postman-newman.yml` — the workflow installs Node, installs newman,
and runs the collection on push/PR. Test artifacts are uploaded as build artifacts.

Environment variables used
--------------------------
- baseUrl = https://restful-booker.herokuapp.com
- username = admin
- password = password123
- token (set at runtime)
- bookingId (set at runtime)
- firstname, lastname (used for randomized test data)

Notes & known quirks
--------------------
- This is a public demo API; some negative inputs can yield 500 Internal Server Error.
  Negative tests in this suite accept 4xx–5xx as "rejection" for stability. Where a 500
  indicates an API bug, I document it under `docs/bugs/`.
- Tests check Content-Type before parsing JSON to avoid runtime errors in Runner/CI.

What reviewers should look for
------------------------------
- Clear folder structure and request naming
- Use of environment variables; no secrets committed
- Chained requests (create → save id → read/update/delete)
- Negative tests and defensive parsing
- CI integration (Newman + GitHub Actions) and artifacts (JUnit/HTML)

If you want to reproduce a failing run
--------------------------------------
- Run collection in Postman Runner; open Postman Console to inspect raw request/response.
- Check `postman/reports/` for CI-generated artifacts.

Contact / Notes
---------------
If anything in the collection is flaky, check the request URL formatting (no spaces, use
`{{baseUrl}}/booking/{{bookingId}}`) and the Postman Console for raw request/response.
