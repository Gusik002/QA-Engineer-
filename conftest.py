import logging
import os
import pathlib
import re
import time
import shutil
from typing import Any, Generator, Optional

import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

_log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
_log_level = getattr(logging, _log_level_name, logging.INFO)
logging.basicConfig(
    level=_log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
_reports_env = os.getenv("REPORTS_DIR")
REPORTS_DIR = pathlib.Path(_reports_env) if _reports_env else PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
(REPORTS_DIR / "downloads").mkdir(parents=True, exist_ok=True)


def _is_truthy(val: Optional[str]) -> bool:
    if val is None:
        return False
    return str(val).lower() in ("1", "true", "yes", "on")


def pytest_addoption(parser) -> None:
    parser.addoption(
        "--phone-number",
        "--phone",
        dest="phone_number",
        action="store",
        default=os.getenv(
            "AZERCELL_PHONE", os.getenv("PHONE_NUMBER", "5XXXXXXXXX")
        ),
        help="Azercell phone number for live tests.",
    )


@pytest.fixture(scope="session")
def phone_number(request) -> str:
    return str(request.config.getoption("phone_number"))


@pytest.fixture(scope="session")
def chrome_options() -> Options:
    """
    ChromeOptions optimized for CI stability and speed.
    """
    opts = Options()

    if _is_truthy(os.getenv("HEADLESS", "1")):
        opts.add_argument("--headless=new")

    chrome_bin = os.getenv("CHROME_BIN")
    if chrome_bin:
        opts.binary_location = chrome_bin

    # Stability-focused flags
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--disable-background-timer-throttling")
    opts.add_argument("--disable-backgrounding-occluded-windows")
    opts.add_argument("--disable-renderer-backgrounding")
    opts.add_argument("--disable-translate")
    opts.add_argument("--disable-popup-blocking")
    opts.add_argument("--disable-features=VizDisplayCompositor")

    opts.add_experimental_option(
        "excludeSwitches", ["enable-logging", "enable-automation"]
    )
    opts.add_experimental_option("useAutomationExtension", False)

    prefs = {
        "download.default_directory": str(REPORTS_DIR / "downloads"),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        "profile.default_content_setting_values.notifications": 2,
    }
    opts.add_experimental_option("prefs", prefs)

    # Only set page_load_strategy if explicitly requested for speed
    if _is_truthy(os.getenv("FAST_PAGE_LOAD", "0")):
        try:
            opts.page_load_strategy = "eager"  # type: ignore[attr-defined]
        except Exception:
            pass

    return opts


def _create_driver(chrome_options: Options) -> WebDriver:
    """
    Create a Chrome WebDriver instance.
    """
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH") or shutil.which(
        "chromedriver"
    )
    service: Optional[Service] = None

    if chromedriver_path:
        log.info("Using chromedriver: %s", chromedriver_path)
        service = Service(chromedriver_path)
    else:
        try:
            log.info("Using webdriver_manager to locate chromedriver...")
            chromedriver_path = ChromeDriverManager().install()
            log.info("ChromeDriver installed at: %s", chromedriver_path)
            service = Service(chromedriver_path)
        except Exception as exc:
            log.warning(
                "webdriver_manager failed (%s), trying default Service()", exc
            )
            service = Service()

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as exc:
        chrome_bin = os.getenv("CHROME_BIN") or getattr(
            chrome_options, "binary_location", None
        )
        raise RuntimeError(
            "Failed to start Chrome WebDriver.\n"
            f"  chromedriver: {chromedriver_path}\n"
            f"  chrome binary: {chrome_bin}\n"
            f"  error: {exc}"
        ) from exc

    # Configurable timeouts
    page_load_timeout = int(os.getenv("PAGE_LOAD_TIMEOUT", "45"))
    driver.set_page_load_timeout(page_load_timeout)

    # Small implicit wait for element discovery (fallback only;
    # prefer explicit waits)
    implicit_wait = float(os.getenv("IMPLICIT_WAIT", "3"))
    driver.implicitly_wait(implicit_wait)

    return driver


@pytest.fixture(scope="session")
def _driver_session(
    chrome_options: Options,
) -> Generator[Optional[WebDriver], None, None]:
    """
    Optional session-scoped driver (enabled via REUSE_BROWSER=1).
    Disabled by default in CI for test isolation.
    """
    reuse = _is_truthy(os.getenv("REUSE_BROWSER", "0"))
    if not reuse:
        yield None
        return

    driver: Optional[WebDriver] = None
    try:
        log.info("Creating session-scoped browser (REUSE_BROWSER=1)")
        driver = _create_driver(chrome_options)
        yield driver
    finally:
        if driver is not None:
            try:
                driver.quit()
                log.info("Session browser quit")
            except Exception:
                log.debug(
                    "Exception while quitting session driver",
                    exc_info=True,
                )


@pytest.fixture()
def browser(
    _driver_session: Optional[WebDriver], chrome_options: Options
) -> Generator[WebDriver, None, None]:
    """
    Browser fixture for tests.
    - If REUSE_BROWSER=1: reuses session driver (faster, less isolated)
    - Otherwise: creates fresh driver per test (default, more stable)
    """
    if _driver_session is not None:
        log.debug("Reusing session browser")
        yield _driver_session
        return

    driver: Optional[WebDriver] = None
    try:
        driver = _create_driver(chrome_options)
        yield driver
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                log.debug(
                    "Exception while quitting function-scoped driver",
                    exc_info=True,
                )


@pytest.fixture()
def wait(browser: WebDriver) -> WebDriverWait:
    """
    Explicit wait helper. Configure WAIT_TIMEOUT (default 15s).
    """
    timeout = int(os.getenv("WAIT_TIMEOUT", "15"))
    return WebDriverWait(browser, timeout=timeout)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(
    item, call
) -> Generator[Any, None, None]:
    outcome: Any = yield
    rep = outcome.get_result()

    if rep.when != "call" or not getattr(rep, "failed", False):
        return

    driver = item.funcargs.get("browser")
    if driver is None:
        return

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    safe_node = re.sub(r"[^\w\-_\.]", "_", item.nodeid)[:150]
    screenshot_path = SCREENSHOTS_DIR / f"{safe_node}_{timestamp}.png"

    try:
        driver.save_screenshot(str(screenshot_path))
        log.info("Screenshot: %s", screenshot_path.name)

        page_source_path = SCREENSHOTS_DIR / f"{safe_node}_{timestamp}.html"
        with open(page_source_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        log.info("Page source: %s", page_source_path.name)
    except Exception:
        log.debug("Failed to save artifacts", exc_info=True)


def pytest_configure(config) -> None:
    config.addinivalue_line("markers", "smoke: quick smoke tests")
    config.addinivalue_line("markers", "regression: regression tests")
    config.addinivalue_line("markers", "slow: slow-running tests")
    config.addinivalue_line("markers", "testcase: external test case ID")
    config.addinivalue_line(
        "markers",
        "flaky: tests that are unstable and may be retried",
    )


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(
    phone_number: str,
) -> Generator[None, None, None]:
    env_name = os.getenv("TEST_ENV", "local")
    base_url = os.getenv(
        "AZERCELL_BASE_URL",
        os.getenv("BASE_URL", "https://www.azercell.com/az/"),
    )

    log.info("=" * 60)
    log.info("Test Environment")
    log.info("  Env: %s", env_name)
    log.info("  Base URL: %s", base_url)
    log.info("  Reports: %s", REPORTS_DIR)
    log.info("  Headless: %s", _is_truthy(os.getenv("HEADLESS", "1")))
    log.info("  Reuse browser: %s", _is_truthy(os.getenv("REUSE_BROWSER", "0")))
    log.info("  Wait timeout: %ss", os.getenv("WAIT_TIMEOUT", "15"))
    log.info(
        "  Page load timeout: %ss", os.getenv("PAGE_LOAD_TIMEOUT", "45")
    )
    masked = (
        "<hidden>"
        if phone_number and phone_number != "5XXXXXXXXX"
        else phone_number
    )
    log.info("  Phone: %s", masked)
    log.info("=" * 60)
    yield
    log.info("Test environment teardown complete")