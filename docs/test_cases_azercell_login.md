# Test cases — Azercell login (public example)

IDs use prefix AZ-LG- for quick reference.

Status: example test cases used for documentation and automation.

AZ-LG-001 — Open home page and reach login
- Type: Positive / smoke
- Precondition: No user session
- Steps:
  1. Open https://www.azercell.com/az/
  2. Click the "Kabinetim" / login link in header
- Expected:
  - New tab/window or navigation to URL containing `kabinetim`
  - Script has switched to login host
- Priority: High
- Automation note: Use `click_login_button()` then assert
  `is_on_login_page()`.

AZ-LG-002 — Enter valid phone number and reach OTP
- Type: Positive
- Precondition: Test phone that accepts OTP (or mocked)
- Steps:
  1. On login page, enter phone `501234567`
  2. Submit (ENTER)
- Expected:
  - Navigation to an OTP / confirm page (URL includes `confirm-number` or `enter-code`)
  - Phone input retains formatted value (leading zero)
- Priority: High
- Automation: `enter_phone_number()` + `submit_phone_number()` +
  check `is_on_otp_page()`.

AZ-LG-003 — Phone normalization
- Type: Unit/utility
- Steps:
  1. Call `normalize_phone_number("0 50-123 4567")`
- Expected: returns `501234567`
- Automation: Call method directly.

AZ-LG-004 — Empty phone field (validation)
- Type: Negative
- Steps:
  1. Clear phone input and submit
- Expected:
  - Inline validation error shown or request blocked
  - No navigation to OTP
- Priority: High
- Automation: assert no OTP navigation and presence of validation message.

AZ-LG-005 — Invalid phone format
- Type: Negative
- Steps:
  1. Enter `abc123` and submit
- Expected:
  - Validation prevents submission; helpful error shown
  - No OTP navigation
- Priority: Medium

AZ-LG-006 — Too long phone number (boundary)
- Type: Boundary
- Steps:
  1. Enter 20+ digits and submit
- Expected:
  - Either truncated input or validation error
- Priority: Low

AZ-LG-007 — Password-change / "forgot password" link navigation
- Type: Positive
- Steps:
  1. On login page, click "şifrəni unutmusunuz" / password-change
- Expected:
  - Navigation to URL containing `password-change`
- Priority: Medium
- Automation: `click_password_change_link()` and assert

AZ-LG-008 — Password change link not present when not logged in (UI robustness)
- Type: Exploratory
- Steps:
  1. Inspect page source / element tree for link availability
- Expected:
  - Either present or gracefully absent (no crash)
- Priority: Low

AZ-LG-009 — Multiple window handling
- Type: Robustness
- Steps:
  1. Click login link if it opens a new window
- Expected:
  - Driver switches to new window where login is served
- Priority: High

AZ-LG-010 — Repeated submit debounce / rate-limiting
- Type: Negative
- Steps:
  1. Submit phone multiple times rapidly
- Expected:
  - UI prevents repeated pushes or server rejects additional attempts with informative message
- Priority: Medium

AZ-LG-011 — Session cookie set after OTP success (manual / integration)
- Type: Integration
- Steps:
  1. Complete OTP successfully (if available)
- Expected:
  - Auth cookie/session present for the login domain
- Priority: High
- Automation: Requires test account or mocked backend.

AZ-LG-012 — Missing locator fallback
- Type: Automation robustness
- Steps:
  1. Simulate changed locator (update page) and check fallback works
- Expected:
  - The test uses alternative locators and still finds control
- Priority: Medium

AZ-LG-013 — Accessibility basics (aria)
- Type: Manual / exploratory
- Steps:
  1. Inspect phone input for `aria-label` or meaningful label
- Expected:
  - Input has an accessible label
- Priority: Low

AZ-LG-014 — XSS-like input handling (security)
- Type: Security (smoke)
- Steps:
  1. Enter `<script>alert(1)</script>` as phone and submit
- Expected:
  - Input is rejected or sanitized; no script executed
- Priority: Medium

AZ-LG-015 — OTP attempt exhaustion
- Type: Negative
- Steps:
  1. Simulate repeated incorrect OTP attempts to hit lockout
- Expected:
  - Proper "too many attempts" message or flow to recovery
- Priority: High
- Notes: Require mocked OTP or a stable test backend.

AZ-LG-016 — Localization: UI language correctness
- Type: Functional / L10n
- Steps:
  1. Verify the login page shows expected Azerbaijani strings
- Expected:
  - Key texts like "Kabinetim", "şifrəni unutmusunuz" present
- Priority: Low

AZ-LG-017 — Browser back / forward behavior
- Type: UX / regression
- Steps:
  1. Navigate from home to login and press browser back
- Expected:
  - App returns to previous page without breaking state
- Priority: Low

AZ-LG-018 — Screenshot on failure (automation policy)
- Type: Process
- Steps:
  1. If a UI test fails, attach screenshot + HTML source
- Expected:
  - CI artifacts include screenshot and minimal page source for triage
- Priority: Process
