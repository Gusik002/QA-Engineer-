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

# Load .env early
load_dotenv()

# Logging configuration (safe convert string to level)
_log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
_log_level = getattr(logging, _log_level_name, logging.INFO)
logging.basicConfig(level=_log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
_reports_env = os.getenv("REPORTS_DIR")
REPORTS_DIR = pathlib.Path(_reports_env) if _reports_env else PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
(REPORTS_DIR / "downloads").mkdir(parents=True, exist_ok=True)


def _is_truthy(val: Optional[str]) -> bool:
    return str(val).lower() in ("1", "true", "yes", "on")


def pytest_addoption(parser) -> None:  # keep parser untyped for pytest compatibility
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
def phone_number(request) -> str:  # keep request untyped to avoid pytest stub issues
    return str(request.config.getoption("phone_number"))


@pytest.fixture(scope="session")
def chrome_options() -> Options:
    """
    Central ChromeOptions optimized for CI speed:
      - headless by default (HEADLESS=0 to disable)
      - disable images, extensions, background throttling
      - set page_load_strategy to eager for faster navigation
    """
    opts = Options()

    if _is_truthy(os.getenv("HEADLESS", "1")):
        # modern headless flag; previous flags still work in many environments
        opts.add_argument("--headless=new")

    # allow specifying a custom Chrome binary (useful on CI)
    chrome_bin = os.getenv("CHROME_BIN")
    if chrome_bin:
        opts.binary_location = chrome_bin

    # common CI-friendly flags
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--disable-background-timer-throttling")
    opts.add_argument("--disable-renderer-backgrounding")
    opts.add_argument("--disable-translate")
    opts.add_argument("--disable-popup-blocking")
    # reduce logging noise
    opts.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    # Preferences: downloads and disable images to speed up page loads
    prefs = {
        "download.default_directory": str(REPORTS_DIR / "downloads"),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        # disable images (two different keys for compatibility)
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.images": 2,
        # disable notifications
        "profile.default_content_setting_values.notifications": 2,
    }
    opts.add_experimental_option("prefs", prefs)

    # Try to set page load strategy to 'eager' (may be ignored on some versions)
    try:
        opts.page_load_strategy = "eager"  # type: ignore[attr-defined]
    except Exception:
        # harmless if not supported
        pass

    return opts


def _create_driver(chrome_options: Options) -> WebDriver:
    """
    Create a Chrome WebDriver instance.
    Lookup order:
      1. CHROMEDRIVER_PATH env var
      2. chromedriver on PATH
      3. webdriver-manager download (cached in ~/.wdm)
    """
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH") or shutil.which("chromedriver")
    service: Optional[Service] = None

    if chromedriver_path:
        log.info("Using chromedriver from: %s", chromedriver_path)
        service = Service(chromedriver_path)
    else:
        # webdriver-manager caches downloads in ~/.wdm so it is reasonably fast on repeated runs
        try:
            log.info("Locating chromedriver via webdriver_manager...")
            chromedriver_path = ChromeDriverManager().install()
            log.info("webdriver_manager provided chromedriver: %s", chromedriver_path)
            service = Service(chromedriver_path)
        except Exception as exc:
            log.warning("webdriver_manager failed: %s — will try default Service()", exc)
            # fallback to Service() and hope a system driver is discoverable
            service = Service()

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as exc:
        chrome_bin = os.getenv("CHROME_BIN", getattr(chrome_options, "binary_location", None))
        raise RuntimeError(
            f"Failed to start Chrome WebDriver (chromedriver={chromedriver_path}, "
            f"chrome_bin={chrome_bin}): {exc}"
        ) from exc

    # Timeouts: configurable via env vars
    page_load_timeout = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))
    try:
        driver.set_page_load_timeout(page_load_timeout)
    except Exception:
        # ignore if driver/version doesn't support it
        pass

    # Prefer explicit waits; keep implicit wait small (default 0)
    implicit_wait = float(os.getenv("IMPLICIT_WAIT", "0"))
    try:
        driver.implicitly_wait(implicit_wait)
    except Exception:
        pass

    return driver


@pytest.fixture(scope="session")
def _driver_session(chrome_options: Options) -> Generator[Optional[WebDriver], None, None]:
    """
    Optional session-scoped driver used when REUSE_BROWSER=1.
    Keeps a single browser instance per pytest worker to dramatically reduce total run time.
    Set REUSE_BROWSER=0 to disable.
    """
    reuse = _is_truthy(os.getenv("REUSE_BROWSER", "1"))
    if not reuse:
        yield None
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
                log.debug("Exception while quitting session driver", exc_info=True)


@pytest.fixture()
def browser(_driver_session: Optional[WebDriver], chrome_options: Options) -> Generator[WebDriver, None, None]:
    """
    Browser fixture used by tests.

    Behaviour:
      - If REUSE_BROWSER=1 (default), yields the session-scoped driver (fast).
      - If REUSE_BROWSER=0, creates a fresh driver per test (isolated).
    """
    if _driver_session is not None:
        # Reuse the session-scoped driver (fast path)
        yield _driver_session
        return

    # Otherwise create a short-lived driver for this test
    driver: Optional[WebDriver] = None
    try:
        driver = _create_driver(chrome_options)
        yield driver
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                log.debug("Exception while quitting function-scoped driver", exc_info=True)


@pytest.fixture()
def wait(browser: WebDriver) -> WebDriverWait:
    """
    Explicit wait helper for tests. Default is small (fast failures).
    Configure WAIT_TIMEOUT env var to increase (seconds).
    """
    timeout = int(os.getenv("WAIT_TIMEOUT", "10"))
    return WebDriverWait(browser, timeout=timeout)


# Hook wrapper must be typed as a generator because it yields.
# Use Any for the yielded outcome so type-checkers won't complain about get_result().
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call) -> Generator[Any, None, None]:
    outcome: Any = yield
    rep = outcome.get_result()

    # Only act on test call phase failures
    if rep.when != "call" or not getattr(rep, "failed", False):
        return

    driver = item.funcargs.get("browser")
    if driver is None:
        return

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    safe_node = re.sub(r"[^\w\-_\.]", "_", item.nodeid)[:200]
    screenshot_name = f"{safe_node}_{timestamp}.png"
    screenshot_path = SCREENSHOTS_DIR / screenshot_name

    try:
        if hasattr(driver, "save_screenshot"):
            driver.save_screenshot(str(screenshot_path))
            log.info("Screenshot saved: %s", screenshot_path)
        else:
            log.debug("Driver has no save_screenshot attribute; skipping screenshot")

        page_source_path = SCREENSHOTS_DIR / f"{safe_node}_{timestamp}.html"
        try:
            with open(page_source_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            log.info("Page source saved: %s", page_source_path)
        except Exception:
            log.debug("Couldn't save page source", exc_info=True)
    except Exception:
        log.exception("Failed to save test artifacts")


def pytest_configure(config) -> None:
    config.addinivalue_line("markers", "smoke: quick smoke tests")
    config.addinivalue_line("markers", "regression: regression tests")
    config.addinivalue_line("markers", "slow: slow-running tests")
    config.addinivalue_line("markers", "testcase: external test case ID (e.g. AZ-LG-001)")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(phone_number: str) -> Generator[None, None, None]:
    """
    Session-level autouse fixture that logs environment details and yields for
    teardown. Keeps the function typed as a Generator to satisfy type checkers.
    """
    log.info("=" * 60)
    log.info("Test Environment Setup")
    log.info("Reports Directory: %s", REPORTS_DIR)
    log.info("Screenshots Directory: %s", SCREENSHOTS_DIR)
    log.info("Headless Mode: %s", _is_truthy(os.getenv("HEADLESS", "1")))
    log.info("REUSE_BROWSER: %s", _is_truthy(os.getenv("REUSE_BROWSER", "1")))
    masked = "<hidden>" if phone_number and phone_number != "5XXXXXXXXX" else phone_number
    log.info("Phone Number (configured): %s", masked)
    log.info("=" * 60)
    yield
    log.info("Test Environment Teardown Complete")