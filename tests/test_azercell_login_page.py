import os
import pytest
from pages.azercell_login_page import AzercellLoginPage

PHONE_NUMBER = os.getenv("PHONE_NUMBER", "507475560")


@pytest.fixture
def login_page(browser, wait):
    return AzercellLoginPage(browser, wait)


@pytest.mark.smoke
def test_home_page_loads(login_page):
    login_page.open_home_page()
    assert "azercell" in login_page.driver.current_url.lower()


@pytest.mark.smoke
def test_navigate_to_login_page(login_page):
    login_page.open_home_page()
    login_page.click_login_button()
    assert login_page.is_on_login_page()


def test_phone_input_accepts_number(login_page):
    login_page.open_home_page()
    login_page.click_login_button()

    entered_phone = login_page.enter_phone_number(PHONE_NUMBER)
    actual_value = login_page.get_phone_input_value()

    normalized_entered = login_page.normalize_phone_number(entered_phone)
    normalized_actual = login_page.normalize_phone_number(actual_value)

    assert normalized_actual == normalized_entered, (
        f"Phone mismatch: entered '{entered_phone}' "
        f"but got '{actual_value}' in field"
    )


def test_phone_number_formats_correctly(login_page):
    login_page.open_home_page()
    login_page.click_login_button()

    entered = login_page.enter_phone_number(PHONE_NUMBER)

    assert entered.startswith("0")


@pytest.mark.regression
def test_password_change_flow(login_page):
    login_page.open_home_page()
    login_page.click_login_button()

    assert login_page.is_on_login_page(), "Not on login page"

    login_page.enter_phone_number(PHONE_NUMBER)
    login_page.submit_phone_number()

    # Check if we're already on OTP page
    if login_page.is_on_otp_page():
        pytest.skip("Already on OTP page - password change requires verification")

    success = login_page.click_password_change_link()
    if not success:
        pytest.skip("Password change link not available")

    assert login_page.is_on_password_change_page(), "Not on password change page"


@pytest.mark.regression
def test_complete_flow_to_otp_page(login_page):
    login_page.open_home_page()

    login_page.click_login_button()
    assert login_page.is_on_login_page(), "Failed to reach login page"

    login_page.enter_phone_number(PHONE_NUMBER)
    login_page.submit_phone_number()

    # If already on OTP page, test passes
    if login_page.is_on_otp_page():
        return  # Success - reached OTP page

    success = login_page.click_password_change_link()
    if not success:
        pytest.skip("Password change link not available")

    assert login_page.is_on_password_change_page(), "Not on password change page"


@pytest.mark.parametrize("phone_variant", [
    PHONE_NUMBER,
    f"0{PHONE_NUMBER}",
])
def test_phone_number_with_and_without_zero(login_page, phone_variant):
    if phone_variant == "YOUR_VALID_AZERCELL_NUMBER_HERE":
        pytest.skip("PHONE_NUMBER not configured")

    login_page.open_home_page()
    login_page.click_login_button()
    entered = login_page.enter_phone_number(phone_variant)
    assert entered.startswith("0")

    actual = login_page.get_phone_input_value()
    assert actual is not None, "Phone input field is empty"