import pytest
from pages.azercell_login_page import AzercellLoginPage

PHONE_NUMBER = "YOUR_VALID_AZERCELL_NUMBER_HERE" #Please use everything after +994, without spaces


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

    success = login_page.click_password_change_link()
    assert success, "Password change link not found"

    assert login_page.is_on_password_change_page(), (
        f"Expected password-change in URL, got: {login_page.driver.current_url}"
    )


@pytest.mark.regression
def test_complete_flow_to_otp_page(login_page):
    login_page.open_home_page()

    login_page.click_login_button()
    assert login_page.is_on_login_page(), "Failed to reach login page"

    login_page.enter_phone_number(PHONE_NUMBER)
    login_page.submit_phone_number()

    success = login_page.click_password_change_link()
    assert success, "Password change link not found"

    assert login_page.is_on_password_change_page(), (
        f"Not on password change page. Current URL: {login_page.driver.current_url}"
    )

    current_url = login_page.driver.current_url
    valid_endpoints = ["confirm-number", "many-code-attempts", "enter-code"]

    assert any(endpoint in current_url for endpoint in valid_endpoints), (
        f"Expected one of {valid_endpoints} in URL, got: {current_url}"
    )


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