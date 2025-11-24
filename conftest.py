import logging
import os
import pathlib
import re
import time
from typing import Generator

import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger(__name__)

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
REPORTS_DIR = pathlib.Path(os.getenv("REPORTS_DIR", PROJECT_ROOT / "reports"))
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def _is_truthy(val: str) -> bool:
    return str(val).lower() in ("1", "true", "yes", "on")

def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--phone-number",
        "--phone",
        dest="phone_number",
        action="store",
        default=os.getenv("AZERCELL_PHONE", os.getenv("PHONE_NUMBER", "5XXXXXXXXX")),
        help=(
            "Azercell phone number for live tests. "
            "Default placeholder causes phone tests to skip."
        ),
    )

@pytest.fixture(scope="session")
def phone_number(request: pytest.FixtureRequest) -> str:
    return str(request.config.getoption("phone_number"))

@pytest.fixture(scope="session")
def chrome_options() -> Options:
    opts = Options()

    headless = _is_truthy(os.getenv("HEADLESS", "1"))
    if headless:
        opts.add_argument("--headless=new")

    chrome_bin = os.getenv("CHROME_BIN")
    if chrome_bin:
        opts.binary_location = chrome_bin

    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-infobars")
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
    driver: WebDriver | None = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)
        yield driver
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"Failed to initialize browser: {exc}")
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass


@pytest.fixture()
def wait(browser: WebDriver) -> WebDriverWait:
    return WebDriverWait(browser, timeout=30)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    outcome = yield
    rep = outcome.get_result()

    if rep.when != "call" or not rep.failed:
        return

    driver: WebDriver | None = item.funcargs.get("browser")
    if driver is None:
        return

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    safe_node = re.sub(r"[^\w\-_\.]", "_", item.nodeid)
    screenshot_name = f"{safe_node}_{timestamp}.png"
    screenshot_path = SCREENSHOTS_DIR / screenshot_name

    try:
        driver.save_screenshot(str(screenshot_path))
        log.info("Screenshot saved: %s", screenshot_path)

        page_source_path = SCREENSHOTS_DIR / f"{safe_node}_{timestamp}.html"
        with open(page_source_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        log.info("Page source saved: %s", page_source_path)
    except Exception as exc:  # noqa: BLE001
        log.exception("Failed to save test artifacts: %s", exc)


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "smoke: quick smoke tests")
    config.addinivalue_line("markers", "regression: regression tests")
    config.addinivalue_line("markers", "slow: slow-running tests")
    config.addinivalue_line(
        "markers",
        "testcase: external test case ID (e.g. AZ-LG-001)",
    )


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(phone_number: str) -> None:
    log.info("=" * 60)
    log.info("Test Environment Setup")
    log.info("=" * 60)
    log.info("Reports Directory: %s", REPORTS_DIR)
    log.info("Screenshots Directory: %s", SCREENSHOTS_DIR)
    log.info("Headless Mode: %s", _is_truthy(os.getenv("HEADLESS", "1")))
    masked = "<hidden>" if phone_number and phone_number != "5XXXXXXXXX" else phone_number
    log.info("Phone Number (configured): %s", masked)
    log.info("=" * 60)
    yield
    log.info("Test Environment Teardown Complete")