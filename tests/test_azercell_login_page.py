import pytest
from pages.azercell_login_page import AzercellLoginPage

# Change this to your Azercell number locally (do not commit real number to Git)
# Or set PHONE_NUMBER environment variable
DEFAULT_PHONE = "5XXXXXXXXX"  # Placeholder - replace locally or use env var


@pytest.fixture()
def login_page(browser, wait):
    return AzercellLoginPage(browser, wait)


@pytest.mark.smoke
def test_home_page_loads(login_page):
    login_page.open_home_page()
    assert "azercell" in login_page.driver.current_url.lower()


@pytest.mark.smoke
def test_login_button_redirects(login_page):
    login_page.open_home_page()
    login_page.click_login_button()
    assert login_page.is_on_login_page(), "Did not reach login page"


@pytest.mark.smoke
def test_phone_input_accepts_number(login_page, phone_number):
    login_page.open_home_page()
    login_page.click_login_button()

    entered_phone = login_page.enter_phone_number(phone_number)
    actual_value = login_page.get_phone_input_value()

    normalized_entered = login_page.normalize_phone_number(entered_phone)
    normalized_actual = login_page.normalize_phone_number(actual_value)

    assert normalized_actual == normalized_entered, (
        f"Phone mismatch: entered '{entered_phone}' "
        f"but got '{actual_value}' in field"
    )


@pytest.mark.regression
def test_phone_submit_navigates_forward(login_page, phone_number):
    login_page.open_home_page()
    login_page.click_login_button()

    initial_url = login_page.driver.current_url

    login_page.enter_phone_number(phone_number)
    login_page.submit_phone_number()

    assert login_page.driver.current_url != initial_url, "URL did not change"


@pytest.mark.regression
def test_password_change_flow(login_page, phone_number):
    login_page.open_home_page()
    login_page.click_login_button()

    assert login_page.is_on_login_page(), "Not on login page"

    login_page.enter_phone_number(phone_number)
    login_page.submit_phone_number()

    # Check if we're already on OTP page
    if login_page.is_on_otp_page():
        pytest.skip("Already on OTP page - password change requires verification")

    success = login_page.click_password_change_link()
    if not success:
        pytest.skip("Password change link not available")

    assert login_page.is_on_password_change_page(), "Not on password change page"


@pytest.mark.regression
def test_complete_flow_to_otp_page(login_page, phone_number):
    login_page.open_home_page()

    login_page.click_login_button()
    assert login_page.is_on_login_page(), "Failed to reach login page"

    login_page.enter_phone_number(phone_number)
    login_page.submit_phone_number()

    # If already on OTP page, test passes
    if login_page.is_on_otp_page():
        return  # Success - reached OTP page

    success = login_page.click_password_change_link()
    if not success:
        pytest.skip("Password change link not available")

    assert login_page.is_on_password_change_page(), "Not on password change page"


@pytest.mark.regression
def test_phone_normalization(login_page):
    test_cases = [
        ("5012345678", "5012345678"),
        ("05012345678", "5012345678"),
        ("50 123 45 678", "5012345678"),
        ("50-123-45-678", "5012345678"),
    ]

    for input_phone, expected in test_cases:
        result = login_page.normalize_phone_number(input_phone)
        assert result == expected, f"Failed for {input_phone}"


@pytest.mark.slow
def test_multiple_phone_formats_accepted(login_page, phone_number):
    login_page.open_home_page()
    login_page.click_login_button()

    formats = [phone_number, f"0{phone_number}" if not phone_number.startswith("0") else phone_number]

    for phone_format in formats:
        login_page.enter_phone_number(phone_format)
        value = login_page.get_phone_input_value()
        assert value is not None and len(value) > 0, (
            f"Phone format {phone_format} not accepted"
        )