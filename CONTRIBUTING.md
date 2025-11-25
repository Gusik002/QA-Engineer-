# Contributing

This repository is mainly a portfolio, but it is structured like a real
team repo. Contributions (PRs, issues, suggestions) are welcome as long
as they keep the codebase clean and focused.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Optional tools for API/performance work:

```bash
npm install -g newman
# k6 is installed via package manager or binary; see k6 docs.
```

## Running checks locally

### Linting (same as CI)

```bash
ruff check pages autotests
black --check pages autotests
```

### UI tests (pytest + Selenium)

Quick smoke run:

```bash
HEADLESS=1 pytest autotests -m smoke -v
```

Smoke + regression:

```bash
HEADLESS=1 pytest autotests -m "smoke or regression" -v
```

If you have a real Azercell test phone number (format `5XXXXXXXXX`):

```bash
export AZERCELL_PHONE="5XXXXXXXXX"
HEADLESS=1 pytest autotests -m "smoke or regression" -v
```

Tests that require a real number will automatically skip if the number
is not configured or left as the placeholder.

### API tests (Postman/Newman)

```bash
newman run postman/collections/restful-booker.postman_collection.json \
  -e postman/environments/restful-booker.postman_environment.json \
  --reporters cli,junit,html \
  --reporter-junit-export reports/api/postman-junit.xml \
  --reporter-html-export reports/api/postman-results.html
```

## Code style and conventions

- Python code must:
  - Pass `ruff` (no new warnings/errors).
  - Be formatted with `black`.
- Tests:
  - One logical scenario per test function.
  - Prefer explicit assertions with custom messages.
  - Use fixtures from `conftest.py` instead of manual driver setup.
- UI tests:
  - Use Page Object Model (keep locators/actions in `pages/`).
  - Avoid raw `time.sleep` where explicit waits are appropriate.

## Secrets and test data

- Never commit real credentials, API keys or real user data.
- Never commit real phone numbers. Use:
  - Local `.env` files (git-ignored).
  - GitHub Actions secrets for CI (e.g. `AZERCELL_PHONE_NUMBER`).
- When you need a new secret in CI:
  - Add it in GitHub → Settings → Secrets and variables → Actions.
  - Reference it via `secrets.MY_SECRET` in workflows.

## Submitting a pull request

1. Create a feature branch:

   ```bash
   git checkout -b feature/my-change
   ```

2. Implement your change and add/adjust tests.
3. Run linters and relevant tests locally.
4. Update documentation if behaviour or flows changed:
   - `docs/test_cases_*.md`
   - `docs/traceability_*.md`
   - Any relevant README files.
5. Open a PR and fill in the PR template:
   - Short summary.
   - List of changes.
   - How you verified them locally.

## CI expectations

- All GitHub Actions jobs should pass before merge:
  - `lint`
  - `ui-tests` (smoke on PRs)
  - `api-tests`
- If a job fails:
  - Check logs and artifacts.
  - Fix the root cause or, if it is unavoidable flakiness, discuss an
    appropriate marking (`xfail`/`flaky`) in the PR.
