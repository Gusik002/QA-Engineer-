import os
import pathlib
import time
from typing import Generator

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


REPORTS_DIR = pathlib.Path(os.getenv("REPORTS_DIR", "../reports"))
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def pytest_addoption(parser):
    parser.addoption(
        "--phone",
        action="store",
        default=os.getenv("PHONE_NUMBER", "5XXXXXXXXX"),
        help="Phone number for Azercell login tests",
    )


@pytest.fixture(scope="session")
def phone_number(request):
    return request.config.getoption("--phone")


@pytest.fixture(scope="session")
def chrome_options() -> Options:
    opts = Options()

    headless = os.getenv("HEADLESS", "1") == "1"
    if headless:
        opts.add_argument("--headless=new")

    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--start-maximized")
    opts.add_argument("--ignore-certificate-errors")

    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    opts.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(REPORTS_DIR / "downloads"),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        },
    )

    return opts


@pytest.fixture()
def browser(chrome_options: Options) -> Generator[WebDriver, None, None]:
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        yield driver
    except Exception as e:
        pytest.fail(f"Failed to initialize browser: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


@pytest.fixture()
def wait(browser: WebDriver) -> WebDriverWait:
    return WebDriverWait(browser, timeout=15)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("browser")
        if driver:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            test_name = item.name.replace("[", "_").replace("]", "")
            screenshot_name = f"{test_name}_{timestamp}.png"
            screenshot_path = SCREENSHOTS_DIR / screenshot_name

            try:
                driver.save_screenshot(str(screenshot_path))
                print(f"\nScreenshot saved: {screenshot_path}")

                page_source_path = SCREENSHOTS_DIR / f"{test_name}_{timestamp}.html"
                with open(page_source_path, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print(f"Page source saved: {page_source_path}")

            except Exception as e:
                print(f"\nFailed to save test artifacts: {e}")


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "regression: mark test as regression test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(phone_number):
    print("\n" + "=" * 60)
    print("Test Environment Setup")
    print("=" * 60)
    print(f"Reports Directory: {REPORTS_DIR}")
    print(f"Screenshots Directory: {SCREENSHOTS_DIR}")
    print(f"Headless Mode: {os.getenv('HEADLESS', '1') == '1'}")
    print(f"Phone Number: {phone_number}")
    print("=" * 60 + "\n")
    yield
    print("\n" + "=" * 60)
    print("Test Environment Teardown Complete")
    print("=" * 60 + "\n")