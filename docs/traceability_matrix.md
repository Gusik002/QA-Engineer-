# Traceability — Azercell Login (public example)

| TC ID    | Feature / Scenario                           | Priority | Automated | Test function                                                       |
|---------|----------------------------------------------|---------:|:---------:|---------------------------------------------------------------------|
| AZ-LG-001 | Open home page and reach login             | High     |   Yes     | `autotests/test_azercell_login_page.py::test_home_page_loads`      |
| AZ-LG-001 | Login button opens login page              | High     |   Yes     | `autotests/test_azercell_login_page.py::test_login_button_redirects` |
| AZ-LG-002 | Enter valid phone and reach OTP step       | High     |   Yes     | `test_phone_input_accepts_number`, `test_complete_flow_to_otp_page` |
| AZ-LG-003 | Phone normalization utility                | Medium   |   Yes     | `test_phone_normalization_unit` + `tests/unit/test_phone_utils.py` |
| AZ-LG-004 | Phone submit navigates forward             | High     |   Yes     | `test_phone_submit_navigates_forward`                              |
| AZ-LG-007 | Password-change / forgot password flow     | Medium   |   Yes     | `test_password_change_flow`                                        |
| AZ-LG-010 | Repeated submits / rate-limiting (formats) | Medium   |   Yes     | `test_multiple_phone_formats_accepted`                             |
| AZ-LG-018 | Screenshot on failure (process)            | Process  |   Yes     | Implemented via `pytest_runtest_makereport` in `conftest.py`       |

When adding or changing a test, update this table and mark the test with
`@pytest.mark.testcase("AZ-LG-XXX")`.