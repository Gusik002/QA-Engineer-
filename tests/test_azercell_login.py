import pytest
from pages.azercell_login_page import AzercellLoginPage

PHONE_NUMBER = "507475560"


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

    assert actual_value == entered_phone


def test_phone_number_formats_correctly(login_page):
    login_page.open_home_page()
    login_page.click_login_button()

    phone_without_zero = "507475560"
    entered = login_page.enter_phone_number(phone_without_zero)

    assert entered.startswith("0")
    assert entered == "0507475560"


@pytest.mark.regression
def test_password_change_flow(login_page):
    login_page.open_home_page()
    login_page.click_login_button()
    login_page.enter_phone_number(PHONE_NUMBER)
    login_page.submit_phone_number()

    success = login_page.click_password_change_link()

    assert success, "Password change link not found"
    assert login_page.is_on_password_change_page()


@pytest.mark.regression
def test_complete_flow_to_otp_page(login_page):
    login_page.open_home_page()

    login_page.click_login_button()
    assert login_page.is_on_login_page()

    login_page.enter_phone_number(PHONE_NUMBER)
    login_page.submit_phone_number()

    login_page.click_password_change_link()
    assert login_page.is_on_password_change_page()

    assert "confirm-number" in login_page.driver.current_url


@pytest.mark.parametrize("phone", [
    "507475560",
    "0507475560",
    "555123456",
])
def test_different_phone_numbers(login_page, phone):
    login_page.open_home_page()
    login_page.click_login_button()
    entered = login_page.enter_phone_number(phone)
    assert entered.startswith("0")