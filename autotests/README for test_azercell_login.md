## Azercell Login Automation
Selenium-based test automation for the Azercell login flow using Python and pytest.
### Prerequisites
- Python 3.10+
- Create and activate a venv (recommended)
- Install deps:
```bash
pip install -r requirements.txt
```
### Configure phone number
You can provide a phone number via environment variable or pytest option:
- Environment:
```bash
export AZERCELL_PHONE="507475560"
export HEADLESS=1    # set to 0 to run with visible browser locally
```
- Or pass on the command line:
```bash
pytest --phone-number=507475560
```
If no phone number is provided the tests that need a real number will automatically skip.

### Quick Start
Run all tests:
```bash
pytest -q
```
Run the single Azercell test file:
```bash
pytest tests/test_azercell_login.py -v
```
Run only smoke tests:
```bash
pytest -m smoke
```
Run a specific test:
```bash
pytest tests/test_azercell_login.py::test_complete_flow_to_otp_page -v
```
### What gets reported on failure
When a test fails, the framework saves:
- Screenshot: `reports/screenshots/<testname>_<ts>.png`
- Page source: `reports/screenshots/<testname>_<ts>.html`
### Files of interest
- tests/test_azercell_login.py — example test scenarios
- pages/azercell_login_page.py — Page Object (skeleton with helpers)
- conftest.py — fixtures: browser, wait, phone_number, screenshot-on-failure hook
- pytest.ini — markers and default config
### Notes for reviewers / recruiters
- To run full UI tests in CI you must ensure Chrome is installed on the runner
  and set `HEADLESS=1`. By default the tests are safe: live phone-number tests
  are skipped unless you set `AZERCELL_PHONE` or `--phone-number`.
