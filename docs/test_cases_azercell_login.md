# Test cases — Azercell login (public example)

IDs use prefix `AZ-LG-` for quick reference.

Status: example test cases used for documentation and automation.

---

AZ-LG-001 — Open home page and reach login
- Type: Positive / smoke
- Precondition: No user session
- Steps:
  1. Open `https://www.azercell.com/az/` (or `/en`).
  2. Click the "Kabinetim" / login link in the header.
- Expected:
  - New tab/window or navigation to a URL containing `kabinetim`.
  - The script has switched to the correct login host if a new window
    was opened.
- Priority: High
- Automation note:
  - `AzercellLoginPage.open_home_page()`
  - `click_login_button()`
  - Assert `is_on_login_page()`.

---

AZ-LG-002 — Enter valid phone number and reach OTP
- Type: Positive
- Precondition:
  - Test phone that is registered and accepts OTP (or mocked backend).
- Steps:
  1. On the login page, enter phone `5012345678` (format `5XXXXXXXXX`).
  2. Submit using the main "Continue"/"Login" button or by pressing
     ENTER.
- Expected:
  - Navigation to an OTP / verification page:
    - URL includes `otp`, `verify` or `verification`, **or**
    - Screen shows 6‑digit code input(s).
  - The phone input retains the value (possibly reformatted).
- Priority: High
- Automation:
  - `enter_phone_number()`, `submit_phone_number()`
  - `is_on_otp_page()` and `is_on_password_change_page()` as fallbacks.

---

AZ-LG-003 — Phone normalization
- Type: Unit/utility
- Steps:
  1. Call `normalize_phone_number("0 50-123 45 678")`.
- Expected:
  - Returns `5012345678`.
- Automation:
  - `test_phone_normalization` in `autotests/test_azercell_login_page.py`
    and (optionally) unit tests in `tests/unit/test_phone_utils.py`.

---

AZ-LG-004 — Empty phone field (validation)
- Type: Negative
- Steps:
  1. On the login page, ensure the phone input is empty.
  2. Submit the form.
- Expected:
  - Inline validation error is shown and/or browser validation kicks in.
  - No navigation to OTP or password-change pages.
- Priority: High
- Automation:
  - Use `has_validation_error()` /
    `get_validation_error_text()` and assert there is no navigation.

---

AZ-LG-005 — Invalid phone format
- Type: Negative
- Steps:
  1. Enter `abc123` as the phone number.
  2. Submit the form.
- Expected:
  - Validation prevents submission; a helpful error is visible.
  - No navigation to OTP.
- Priority: Medium

---

AZ-LG-006 — Too long phone number (boundary)
- Type: Boundary
- Steps:
  1. Enter a very long phone (e.g. 20+ digits).
  2. Submit the form.
- Expected:
  - Either the input is truncated, or a validation message appears.
  - No OTP navigation with invalid data.
- Priority: Low

---

AZ-LG-007 — Password-change / "forgot password" link navigation
- Type: Positive
- Steps:
  1. On the login page, click the "şifrəni unutmusunuz" /
     "Forgot password" / password-change link.
- Expected:
  - Navigation to a URL containing `password`, `reset` or `sifrə`.
- Priority: Medium
- Automation:
  - `click_password_change_link()`
  - Assert `is_on_password_change_page()`.

---

AZ-LG-008 — Password change link not present (UI robustness)
- Type: Exploratory
- Steps:
  1. Inspect the login page for the presence of a password-change link.
- Expected:
  - Link is either present and functional, or cleanly absent (no broken
    UI, exceptions or dead links).
- Priority: Low

---

AZ-LG-009 — Multiple window handling
- Type: Robustness
- Steps:
  1. From the home page, click the login link.
  2. If the site opens the login in a new tab/window, ensure the
     automation switches context correctly.
- Expected:
  - Driver is on the login page host after the click.
- Priority: High
- Automation:
  - Uses `switch_to_new_window()` inside `click_login_button()`.

---

AZ-LG-010 — Repeated submit debounce / rate-limiting
- Type: Negative
- Steps:
  1. Enter a valid phone.
  2. Press the submit button multiple times rapidly.
- Expected:
  - UI prevents repeated submissions (button disabled/spinner), **or**
  - Server rejects additional attempts with a clear message.
- Priority: Medium
- Automation:
  - Covered partially by `test_multiple_phone_formats_accepted` and
    submit behaviour in regression tests.

---

AZ-LG-011 — Session cookie set after OTP success (manual / integration)
- Type: Integration
- Steps:
  1. Complete OTP successfully (using a real test account).
  2. Inspect cookies/storage for the login domain.
- Expected:
  - Auth cookie/session is present and scoped correctly.
- Priority: High
- Automation:
  - Requires test account or mocked backend; not fully automated in
    this public example.

---

AZ-LG-012 — Missing locator fallback
- Type: Automation robustness
- Steps:
  1. Simulate a changed locator for the login link or submit button.
  2. Check that fallback selectors still find the correct control.
- Expected:
  - Automation continues to work via alternative selectors.
- Priority: Medium

---

AZ-LG-013 — Accessibility basics (ARIA / labels)
- Type: Manual / exploratory
- Steps:
  1. Inspect the phone input for an accessible name:
     - Label element
     - `aria-label` or `aria-labelledby`.
- Expected:
  - Input has a meaningful accessible label.
- Priority: Low

---

AZ-LG-014 — XSS-like input handling (security)
- Type: Security (smoke)
- Steps:
  1. Enter `<script>alert(1)</script>` as the phone and submit.
- Expected:
  - Input is validated or safely rejected; no script execution.
- Priority: Medium

---

AZ-LG-015 — OTP attempt exhaustion
- Type: Negative
- Steps:
  1. On the OTP screen, deliberately enter incorrect codes repeatedly
     until lockout (if implemented).
- Expected:
  - Proper "too many attempts" message or flow to recovery.
- Priority: High
- Notes:
  - Requires stable test backend or mocking to avoid impacting real
    users.

---

AZ-LG-016 — Localization: UI language correctness
- Type: Functional / L10n
- Steps:
  1. Verify that the login page shows expected Azerbaijani or English
     strings depending on the language variant.
- Expected:
  - Key texts like "Kabinetim", "şifrəni unutmusunuz" (for AZ) or
    equivalent EN texts are shown correctly.
- Priority: Low

---

AZ-LG-017 — Browser back / forward behaviour
- Type: UX / regression
- Steps:
  1. Navigate from home to login.
  2. Click browser Back, then Forward.
- Expected:
  - Application returns to previous page without broken state.
  - Login page still functions after forward navigation.
- Priority: Low

---

AZ-LG-018 — Screenshot on failure (automation policy)
- Type: Process
- Steps:
  1. Trigger a failing UI test.
  2. Inspect CI artifacts.
- Expected:
  - CI artifacts include screenshot PNG and HTML page source for each
    failed UI test.
- Priority: Process
- Automation:
  - Implemented via `pytest_runtest_makereport` hook in `conftest.py`.