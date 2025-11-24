import logging
import time
from typing import Tuple, Union

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

log = logging.getLogger(__name__)
Locator = Union[Tuple[str, str], str]


class BasePage:
    def __init__(self, driver: WebDriver, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait

    def open(self, url: str) -> None:
        self.driver.get(url)

    def click(self, locator: Locator, retries: int = 2, delay: float = 0.3) -> bool:
        """Optimized click with reduced retries and delays."""
        if isinstance(locator, str):
            by, value = By.CSS_SELECTOR, locator
        elif isinstance(locator, (tuple, list)) and len(locator) == 2:
            by, value = locator
        else:
            log.error("Invalid locator: %r", locator)
            return False

        for attempt in range(1, retries + 1):
            try:
                el = self.wait.until(EC.element_to_be_clickable((by, value)))
                el.click()
                return True
            except (ElementClickInterceptedException, StaleElementReferenceException):
                if attempt < retries:
                    time.sleep(delay)
            except TimeoutException:
                break

        # JS fallback
        try:
            el = self.driver.find_element(by, value)
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'instant'}); "
                "arguments[0].click();",
                el
            )
            return True
        except Exception as exc:
            log.warning("Click failed for %s: %s", (by, value), exc)
            return False

    def switch_to_new_window(self) -> bool:
        handles = self.driver.window_handles
        if len(handles) > 1:
            self.driver.switch_to.window(handles[-1])
            return True
        return False