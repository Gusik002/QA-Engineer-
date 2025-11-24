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
Locator = Union[Tuple[str, str], str]  # accept ("by", "value") or "css selector" string


class BasePage:
    def __init__(self, driver: WebDriver, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait

    def open(self, url: str) -> None:
        self.driver.get(url)

    def click(self, locator: Locator, retries: int = 3, delay: float = 0.5) -> bool:
        """
        Robust click helper.
        Accepts either a locator tuple (By.<METHOD>, "value") or a CSS selector string.
        Returns True on success, False on failure (no exception raised).
        """
        # Normalize locator to (by, value)
        if isinstance(locator, str):
            by, value = By.CSS_SELECTOR, locator
        elif isinstance(locator, (tuple, list)) and len(locator) == 2:
            by, value = locator  # type: ignore[assignment]
        else:
            log.error("Invalid locator passed to click(): %r", locator)
            return False

        # try explicit clickable + click with retries
        for attempt in range(1, retries + 1):
            try:
                el = self.wait.until(EC.element_to_be_clickable((by, value)))
                el.click()
                return True
            except (ElementClickInterceptedException, StaleElementReferenceException) as exc:
                log.debug("Click attempt %s/%s failed for %s: %s", attempt, retries, (by, value), exc)
                self._wait_for_overlays()
                time.sleep(delay)
            except TimeoutException as exc:
                log.debug("Timeout waiting for clickable %s: %s", (by, value), exc)
                time.sleep(delay)

        # Final fallback: find and JS click (use explicit by/value to avoid splat issues)
        try:
            el = self.driver.find_element(by, value)
            # scroll into view then JS click
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            self.driver.execute_script("arguments[0].click();", el)
            return True
        except NoSuchElementException:
            log.warning("Element not found for locator %s", (by, value))
            return False
        except Exception as exc:
            log.exception("JS click fallback failed for %s: %s", (by, value), exc)
            return False

    def _wait_for_overlays(self, timeout: float = 2.0) -> None:
        """
        Short wait for common overlays (cookie banners, modals) to disappear.
        """
        overlays_locator = (By.CSS_SELECTOR, ".cookie-banner, .modal, .overlay, .cc-window, .cookie-consent")
        try:
            WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located(overlays_locator))
        except Exception:
            # ignore: overlay may not exist or not vanish quickly
            pass

    def switch_to_new_window(self) -> bool:
        handles = self.driver.window_handles
        if len(handles) > 1:
            self.driver.switch_to.window(handles[-1])
            return True
        return False