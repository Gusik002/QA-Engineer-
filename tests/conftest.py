import os
import pathlib
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")
pathlib.Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True)

@pytest.fixture(scope="session")
def chrome_options():
    opts = Options()
    if os.getenv("HEADLESS", "1") == "1":
        opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    return opts

@pytest.fixture()
def browser(chrome_options):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    yield driver
    driver.quit()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.failed:
        driver = item.funcargs.get("browser")
        if driver:
            test_name = item.name
            dest = f"{REPORTS_DIR}/{test_name}.png"
            try:
                driver.save_screenshot(dest)
            except Exception:
                pass
