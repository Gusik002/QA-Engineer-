import time
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class AzercellLoginPage:
    BASE_URL = "https://www.azercell.com/az/"
    LOGIN_URL = "https://kabinetim.azercell.com/my/login"

    LOGIN_BUTTON_LOCATORS = [
        (By.XPATH, '//a[contains(@href, "kabinetim.azercell.com")]'),
        (By.CSS_SELECTOR, 'a[href*="kabinetim"]'),
        (By.PARTIAL_LINK_TEXT, "Kabinetim"),
    ]

    PHONE_INPUT_LOCATORS = [
        (By.CSS_SELECTOR, "input.az-input-field"),
        (By.XPATH, '//input[contains(@class, "az-input-field")]'),
        (By.CSS_SELECTOR, "input[type='tel']"),
        (By.CSS_SELECTOR, "input[type='text']"),
    ]

    PASSWORD_CHANGE_LOCATORS = [
        (By.XPATH, '//a[contains(@href, "password-change")]'),
        (By.PARTIAL_LINK_TEXT, "şifrəni unutmusunuz"),
        (By.CSS_SELECTOR, 'a[href*="password-change"]'),
    ]

    def __init__(self, driver: WebDriver, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait

    def find_element_by_multiple_locators(
            self, locators: list[tuple], timeout: int = 15
    ):
        wait = WebDriverWait(self.driver, timeout)
        for by, value in locators:
            try:
                return wait.until(EC.element_to_be_clickable((by, value)))
            except TimeoutException:
                continue
        raise NoSuchElementException(
            "Could not find element with any provided locators"
        )

    def open_home_page(self):
        self.driver.get(self.BASE_URL)

    def click_login_button(self):
        initial_handles = set(self.driver.window_handles)
        login_button = self.find_element_by_multiple_locators(
            self.LOGIN_BUTTON_LOCATORS
        )
        login_button.click()
        time.sleep(1)
        self._switch_to_new_window_if_needed(initial_handles)

    def _switch_to_new_window_if_needed(self, initial_handles: set):
        try:
            WebDriverWait(self.driver, 5).until(
                lambda d: len(d.window_handles) > len(initial_handles)
                          or "kabinetim" in d.current_url
            )
            current_handles = set(self.driver.window_handles)
            new_handles = current_handles - initial_handles
            if new_handles:
                self.driver.switch_to.window(new_handles.pop())
        except TimeoutException:
            pass

    def enter_phone_number(self, phone: str):
        phone_formatted = phone if phone.startswith("0") else f"0{phone}"
        phone_input = self.find_element_by_multiple_locators(
            self.PHONE_INPUT_LOCATORS
        )
        phone_input.clear()
        time.sleep(0.3)
        phone_input.send_keys(phone_formatted)
        time.sleep(0.5)
        return phone_formatted

    def submit_phone_number(self):
        phone_input = self.find_element_by_multiple_locators(
            self.PHONE_INPUT_LOCATORS
        )
        phone_input.send_keys(Keys.ENTER)
        time.sleep(2)

    def click_password_change_link(self) -> bool:
        try:
            change_link = self.find_element_by_multiple_locators(
                self.PASSWORD_CHANGE_LOCATORS, timeout=10
            )
            change_link.click()
            time.sleep(2)

            try:
                WebDriverWait(self.driver, 10).until(
                    lambda d: "password-change" in d.current_url
                )
            except TimeoutException:
                pass

            return True
        except NoSuchElementException:
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
        normalized = phone.replace(" ", "").replace("-", "").lstrip("0")
        return normalized