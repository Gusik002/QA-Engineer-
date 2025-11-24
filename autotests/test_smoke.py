import pytest

from pages.azercell_login_page import AzercellLoginPage


@pytest.fixture()
def login_page(browser, wait) -> AzercellLoginPage:
    return AzercellLoginPage(browser, wait)


@pytest.mark.smoke
def test_smoke_home_and_login(login_page: AzercellLoginPage) -> None:
    """
    Smoke test: navigate directly to login page and verify.
    Using direct navigation for speed and reliability in CI.
    """
    login_page.open_login_page_directly()
    assert login_page.is_on_login_page(), "Failed to reach login page"