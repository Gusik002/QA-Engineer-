import pytest

from pages.azercell_login_page import AzercellLoginPage


@pytest.fixture()
def login_page(browser, wait) -> AzercellLoginPage:
    return AzercellLoginPage(browser, wait)


@pytest.mark.smoke
def test_smoke_home_and_login(login_page: AzercellLoginPage) -> None:
    login_page.open_home_page()
    login_page.click_login_button()
    assert login_page.is_on_login_page()