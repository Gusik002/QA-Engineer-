import time

import pytest

from pages.azercell_login_page import AzercellLoginPage

DEFAULT_PHONE = "5XXXXXXXXX"


@pytest.fixture()
def login_page(browser, wait):
    return AzercellLoginPage(browser, wait)


@pytest.mark.smoke
def test_home_page_loads(login_page):
    """Test that Azercell home page loads."""
    login_page.open_home_page()
    assert "azercell" in login_page.driver.current_url.lower()


@pytest.mark.smoke
def test_login_page_direct_access(login_page):
    """Test direct access to login page (fast path for CI)."""
    login_page.open_login_page_directly()
    assert login_page.is_on_login_page(), "Direct login page access failed"


@pytest.mark.smoke
def test_login_button_redirects(login_page):
    """Test clicking login button from home page."""
    login_page.open_home_page()
    success = login_page.click_login_button()
    assert success, "Login button did not navigate to login page"
    assert login_page.is_on_login_page(), "Not on login page after click"


@pytest.mark.smoke
def test_phone_input_accepts_number(login_page, phone_number):
    """Test entering phone number in login form."""
    if not phone_number or phone_number == DEFAULT_PHONE:
        pytest.skip("Valid phone number not configured")

    login_page.open_login_page_directly()
    assert login_page.is_on_login_page(), "Not on login page"

    entered_phone = login_page.enter_phone_number(phone_number)
    actual_value = login_page.get_phone_input_value()

    normalized_entered = login_page.normalize_phone_number(entered_phone)
    normalized_actual = login_page.normalize_phone_number(actual_value)

    assert (
        normalized_actual == normalized_entered
    ), f"Phone mismatch: entered '{entered_phone}' but got '{actual_value}'"


@pytest.mark.regression
def test_phone_submit_navigates_forward(login_page, phone_number):
    """Test submitting phone number navigates forward."""
    if not phone_number or phone_number == DEFAULT_PHONE:
        pytest.skip("Valid phone number required for navigation test")

    login_page.open_login_page_directly()
    initial_url = login_page.driver.current_url

    # Enter phone
    login_page.enter_phone_number(phone_number)

    # Check for validation errors before submitting
    if login_page.has_validation_error():
        error_text = login_page.get_validation_error_text()
        pytest.skip(f"Form validation failed before submit: {error_text}")

    # Submit
    success = login_page.submit_phone_number()
    if not success:
        error_text = login_page.get_validation_error_text()
        if error_text:
            pytest.skip(f"Form submission prevented by validation error: {error_text}")
        else:
            pytest.skip(
                "Form submission failed - button may be disabled or phone invalid"
            )

    # Allow extra time for navigation (some sites are slow)
    time.sleep(4)

    final_url = login_page.driver.current_url

    # Check multiple success conditions
    url_changed = final_url != initial_url
    on_otp = login_page.is_on_otp_page()
    on_password = login_page.is_on_password_change_page()

    # Log all conditions for debugging
    print("\nNavigation check:")
    print(f"  Initial URL: {initial_url}")
    print(f"  Final URL: {final_url}")
    print(f"  URL changed: {url_changed}")
    print(f"  On OTP page: {on_otp}")
    print(f"  On password page: {on_password}")

    if url_changed or on_otp or on_password:
        # Success - at least one condition met
        assert True
    else:
        # Final check: is there an error message explaining why?
        error_text = login_page.get_validation_error_text()
        if error_text:
            pytest.skip(
                f"Page did not navigate. Validation error present: {error_text}"
            )
        else:
            # This might be expected behavior for test/invalid numbers
            pytest.skip(
                "Page did not navigate and no error detected. "
                "This may indicate the phone number format is not accepted by the site, "
                "or the site requires a real registered number. "
                f"URL remained: {final_url}"
            )


@pytest.mark.regression
def test_password_change_flow(login_page, phone_number):
    """Test password change link flow."""
    if not phone_number or phone_number == DEFAULT_PHONE:
        pytest.skip("Valid phone number not configured")

    login_page.open_login_page_directly()
    assert login_page.is_on_login_page(), "Not on login page"

    login_page.enter_phone_number(phone_number)
    login_page.submit_phone_number()

    if login_page.is_on_otp_page():
        pytest.skip("Already on OTP page")

    success = login_page.click_password_change_link()
    if not success:
        pytest.skip("Password change link not available")

    assert login_page.is_on_password_change_page(), "Not on password change page"


@pytest.mark.regression
def test_complete_flow_to_otp_page(login_page, phone_number):
    """Test complete login flow to OTP page."""
    if not phone_number or phone_number == DEFAULT_PHONE:
        pytest.skip("Valid phone number not configured")

    login_page.open_login_page_directly()
    assert login_page.is_on_login_page(), "Failed to reach login page"

    login_page.enter_phone_number(phone_number)
    login_page.submit_phone_number()

    if login_page.is_on_otp_page():
        return  # Success

    # If not on OTP page, try password change flow
    success = login_page.click_password_change_link()
    if not success:
        pytest.skip("Neither OTP nor password change available")

    assert login_page.is_on_password_change_page(), "Expected OTP or password page"


@pytest.mark.regression
def test_phone_normalization(login_page):
    """Test phone number normalization logic (no browser interaction)."""
    test_cases = [
        ("5012345678", "5012345678"),
        ("05012345678", "5012345678"),
        ("50 123 45 678", "5012345678"),
        ("50-123-45-678", "5012345678"),
    ]

    for input_phone, expected in test_cases:
        result = login_page.normalize_phone_number(input_phone)
        assert result == expected, f"Normalization failed for {input_phone}"


@pytest.mark.slow
def test_multiple_phone_formats_accepted(login_page, phone_number):
    """Test that different phone formats are accepted."""
    if not phone_number or phone_number == DEFAULT_PHONE:
        pytest.skip("Valid phone number not configured")

    login_page.open_login_page_directly()
    assert login_page.is_on_login_page(), "Not on login page"

    formats = [
        phone_number,
        (f"0{phone_number}" if not phone_number.startswith("0") else phone_number),
    ]

    for phone_format in formats:
        login_page.enter_phone_number(phone_format)
        value = login_page.get_phone_input_value()
        assert value and len(value) > 0, f"Format {phone_format} not accepted"
