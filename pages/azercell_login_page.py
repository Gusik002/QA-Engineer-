import logging
import time
from typing import Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.phone import normalize_phone_number

log = logging.getLogger(__name__)


class AzercellLoginPage(BasePage):
    BASE_URL = "https://www.azercell.com/az/"

    LOGIN_LINK = (By.CSS_SELECTOR, "a[href*='kabinetim'], a[href*='cabinet'], a[href*='login']")
    PHONE_INPUT = (By.CSS_SELECTOR, "input[type='tel'], input[name*='phone'], input[id*='phone']")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit'], button.send-otp")
    PASSWORD_CHANGE_LINK = (
        By.XPATH,
        "//a[contains(translate(., 'ŞİFRƏNI UNUTMUSUNUZ', 'şifrəni unutmusunuz'), 'şifrəni unutmusunuz') "
        "or contains(., 'Forgot password') or contains(., 'password-change')]",
    )
    OTP_INDICATOR = (By.CSS_SELECTOR, "input[name*='otp'], input[id*='otp'], input[name*='code']")

    def open_home_page(self) -> None:
        self.open(self.BASE_URL)

    def click_login_button(self) -> bool:
        """
        Click the login link. If a new tab/window opens, switch to it.
        Returns True on success (clicked and switched if needed), False on failure.
        """
        clicked = self.click(self.LOGIN_LINK)
        if not clicked:
            log.warning("click_login_button: initial click failed for %s", self.LOGIN_LINK)
            return False

        # Wait shortly for a new window and switch if it appears
        try:
            WebDriverWait(self.driver, 2).until(lambda d: len(d.window_handles) > 1)
            self.switch_to_new_window()
        except TimeoutException:
            # no new window appeared — that's OK
            pass

        return True

    def is_on_login_page(self) -> bool:
        try:
            self.wait.until(EC.presence_of_element_located(self.PHONE_INPUT))
            return True
        except Exception:
            # fallback check by URL string
            return "kabinetim" in self.driver.current_url.lower() or "login" in self.driver.current_url.lower()

    def enter_phone_number(self, phone: str) -> str:
        phone = str(phone)
        el = self.wait.until(EC.visibility_of_element_located(self.PHONE_INPUT))
        el.clear()
        el.send_keys(phone)
        return phone

    def get_phone_input_value(self) -> str | None:
        try:
            by, value = self.PHONE_INPUT
            el = self.driver.find_element(by, value)
            return el.get_attribute("value") or ""
        except Exception:
            return None

    def submit_phone_number(self) -> bool:
        """
        Try clicking the submit button; if that fails, fall back to pressing ENTER
        in the phone input. Returns True if submission was attempted, False otherwise.
        """
        if self.click(self.SUBMIT_BUTTON):
            return True

        # fallback: press Enter in the phone input
        try:
            by, value = self.PHONE_INPUT
            input_el = self.driver.find_element(by, value)
            input_el.send_keys(Keys.ENTER)
            return True
        except Exception as exc:
            log.exception("submit_phone_number fallback failed: %s", exc)
            return False

    def is_on_otp_page(self) -> bool:
        try:
            if "otp" in self.driver.current_url.lower():
                return True
            elements = self.driver.find_elements(*self.OTP_INDICATOR)
            return bool(elements)
        except Exception:
            return False

    def click_password_change_link(self) -> bool:
        return self.click(self.PASSWORD_CHANGE_LINK)

    def is_on_password_change_page(self) -> bool:
        url = self.driver.current_url.lower()
        return "password" in url or "reset" in url

    @staticmethod
    def normalize_phone_number(phone: str | None) -> str:
        return normalize_phone_number(phone)