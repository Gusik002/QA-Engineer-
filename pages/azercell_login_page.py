"""
Azercell login page object.

Purpose:
- Demonstrate a robust Page Object for the Azercell public login flow.
- Includes multiple locator fallbacks, explicit waits and helpful logging.
"""

from __future__ import annotations
import logging
import time
from typing import Optional, Tuple
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

Locator = Tuple[str, str]

class AzercellLoginPage:
    BASE_URL = "https://www.azercell.com/az/"
    LOGIN_URL = "https://kabinetim.azercell.com/my/login"
    DEFAULT_TIMEOUT = 20

    LOGIN_BUTTON_LOCATORS: list[Locator] = [
        (By.XPATH, '//a[contains(@href, "kabinetim.azercell.com")]'),
        (By.CSS_SELECTOR, 'a[href*="kabinetim"]'),
        (By.PARTIAL_LINK_TEXT, "Kabinetim"),
    ]

    PHONE_INPUT_LOCATORS: list[Locator] = [
        (By.CSS_SELECTOR, "input.az-input-field"),
        (By.XPATH, '//input[contains(@class, "az-input-field")]'),
        (By.CSS_SELECTOR, "input[type='tel']"),
        (By.CSS_SELECTOR, "input[type='text']"),
    ]

    PASSWORD_CHANGE_LOCATORS: list[Locator] = [
        (By.XPATH, '//a[contains(@href, "password-change")]'),
        (By.PARTIAL_LINK_TEXT, "şifrəni unutmusunuz"),
        (By.CSS_SELECTOR, 'a[href*="password-change"]'),
    ]

    def __init__(self, driver: WebDriver, wait_timeout: int | None = None) -> None:
        self.driver = driver
        self.wait_timeout = wait_timeout or self.DEFAULT_TIMEOUT

    def _wait(self, timeout: int | None = None) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout or self.wait_timeout)

    def find_element_by_multiple_locators(
        self, locators: list[Locator], timeout: int | None = None
    ) -> WebElement:
        """
        Try each locator in order and return the first clickable element.
        Raises NoSuchElementException if none found within total timeout.
        """
        total_timeout = timeout or self.wait_timeout
        deadline = time.time() + total_timeout
        last_exc: Optional[Exception] = None

        for by, value in locators:
            remaining = max(0.5, deadline - time.time())
            try:
                elem = WebDriverWait(self.driver, remaining).until(
                    EC.element_to_be_clickable((by, value))
                )
                logger.debug("Found element by %s: %s", by, value)
                return elem
            except TimeoutException as exc:
                last_exc = exc
                logger.debug("Locator timed out: %s %s", by, value)
                continue

        logger.debug("No locator matched after %s sec", total_timeout)
        raise NoSuchElementException(
            "Could not find element with any of the provided locators"
        ) from last_exc

    def open_home_page(self) -> None:
        self.driver.get(self.BASE_URL)
        try:
            self._wait(10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            logger.debug("Home page did not reach readyState=complete in 10s")

    def click_login_button(self) -> None:
        initial_handles = set(self.driver.window_handles)

        try:
            self._wait(10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            login_button = self.find_element_by_multiple_locators(
                self.LOGIN_BUTTON_LOCATORS, timeout=20
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", login_button
            )
            time.sleep(0.5)

            try:
                login_button.click()
            except Exception:
                logger.debug("Regular click failed, trying JS click")
                self.driver.execute_script("arguments[0].click();", login_button)

            time.sleep(1)
            self._switch_to_new_window_if_needed(initial_handles)

        except Exception as exc:
            logger.exception("Error clicking login button: %s", exc)
            logger.debug("Current URL: %s", self.driver.current_url)
            raise

    def _switch_to_new_window_if_needed(self, initial_handles: set[str]) -> None:
        """
        Switch to a newly opened window/tab if it appears or if the URL
        contains the login host.
        """
        try:
            WebDriverWait(self.driver, 8).until(
                lambda d: len(d.window_handles) > len(initial_handles)
                or "kabinetim" in d.current_url
            )
            current_handles = set(self.driver.window_handles)
            new_handles = current_handles - initial_handles
            if new_handles:
                self.driver.switch_to.window(new_handles.pop())
                time.sleep(0.3)
        except TimeoutException:
            logger.debug("No new window opened and no kabinetim URL found")

    def enter_phone_number(self, phone: str) -> str:
        """
        Formats phone and types into the phone input. Returns formatted
        phone used for further assertions.
        """
        phone_formatted = phone if phone.startswith("0") else f"0{phone}"
        phone_input = self.find_element_by_multiple_locators(
            self.PHONE_INPUT_LOCATORS, timeout=15
        )
        phone_input.clear()
        time.sleep(0.15)
        phone_input.send_keys(phone_formatted)
        time.sleep(0.15)
        return phone_formatted

    def submit_phone_number(self) -> None:
        phone_input = self.find_element_by_multiple_locators(
            self.PHONE_INPUT_LOCATORS, timeout=8
        )
        phone_input.send_keys(Keys.ENTER)
        try:
            self._wait(5).until(
                lambda d: "confirm" in d.current_url or "enter-code" in d.current_url
            )
        except TimeoutException:
            logger.debug("Submit did not change URL within 5s")

    def click_password_change_link(self) -> bool:
        """
        Click the "password change / forgot password" link.
        Returns True if click sequence executed (even if navigation not completed).
        """
        try:
            time.sleep(0.5)
            change_link = self.find_element_by_multiple_locators(
                self.PASSWORD_CHANGE_LOCATORS, timeout=12
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", change_link
            )
            time.sleep(0.15)
            try:
                change_link.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", change_link)

            try:
                self._wait(10).until(lambda d: "password-change" in d.current_url)
            except TimeoutException:
                logger.debug("Password change nav not confirmed in 10s")
            return True
        except (NoSuchElementException, TimeoutException) as exc:
            logger.debug("Password change link not available: %s", exc)
            logger.debug("Current URL: %s", self.driver.current_url)
            logger.debug("Page source slice: %s", self.driver.page_source[:200])
            return False

    def is_on_password_change_page(self) -> bool:
        return "password-change" in self.driver.current_url

    def is_on_login_page(self) -> bool:
        return "kabinetim" in self.driver.current_url

    def is_on_otp_page(self) -> bool:
        current_url = self.driver.current_url
        return any(
            endpoint in current_url
            for endpoint in ["confirm-number", "enter-code", "many-code-attempts"]
        )

    def get_phone_input_value(self) -> Optional[str]:
        try:
            phone_input = self.find_element_by_multiple_locators(
                self.PHONE_INPUT_LOCATORS, timeout=5
            )
            return phone_input.get_attribute("value")
        except NoSuchElementException:
            return None

    def normalize_phone_number(self, phone: str) -> str:
        """Return digits-only phone without leading zeros."""
        normalized = phone.replace(" ", "").replace("-", "").lstrip("0")
        return normalized
