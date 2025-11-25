# Traceability — Azercell Login (public example)

Mapping between documented test cases (AZ‑LG‑*) and automated tests.

| TC ID     | Feature / Scenario                           | Priority | Automated | Test function(s)                                                                                      |
|-----------|----------------------------------------------|---------:|:---------:|--------------------------------------------------------------------------------------------------------|
| AZ-LG-001 | Open home page and reach login               |    High |    Yes    | `autotests/test_azercell_login_page.py::test_home_page_loads`                                         |
| AZ-LG-001 | Login button opens login page                |    High |    Yes    | `autotests/test_azercell_login_page.py::test_login_button_redirects`                                  |
| AZ-LG-001 | Direct navigation to login (smoke)           |    High |    Yes    | `autotests/test_smoke.py::test_smoke_home_and_login`                                                  |
| AZ-LG-002 | Enter valid phone and reach OTP / next step  |    High |    Yes    | `autotests/test_azercell_login_page.py::test_phone_submit_navigates_forward`                          |
| AZ-LG-002 | Complete flow towards OTP / password-change  |    High |    Yes    | `autotests/test_azercell_login_page.py::test_complete_flow_to_otp_page`                               |
| AZ-LG-003 | Phone normalization utility                  |  Medium |    Yes    | `autotests/test_azercell_login_page.py::test_phone_normalization`                                     |
| AZ-LG-004 | Phone submit navigates forward / validation  |    High |    Yes    | `autotests/test_azercell_login_page.py::test_phone_submit_navigates_forward`                          |
| AZ-LG-007 | Password-change / forgot password flow       |  Medium |    Yes    | `autotests/test_azercell_login_page.py::test_password_change_flow`                                    |
| AZ-LG-010 | Multiple phone formats accepted              |  Medium |    Yes    | `autotests/test_azercell_login_page.py::test_multiple_phone_formats_accepted`                         |
| AZ-LG-012 | Multiple window handling (login opens new tab)|   High |    Yes    | Implemented via `pages/base_page.py::BasePage.switch_to_new_window()` used in `click_login_button()`  |
| AZ-LG-018 | Screenshot on failure (process)              | Process |    Yes    | Implemented via `pytest_runtest_makereport` hook in `conftest.py`                                     |

Notes:

- A single automated test can cover multiple test cases (e.g. navigation
  + validation).
- Some negative and exploratory scenarios (e.g. XSS, ARIA/accessibility)
  are intentionally not fully automated in this public repo.
- When adding or changing a test, update this table and consider
  marking the test with `@pytest.mark.testcase("AZ-LG-XXX")`.