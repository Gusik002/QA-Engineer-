import logging

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

    LOGIN_LINK = (By.CSS_SELECTOR, "a[href*='kabinetim'], a[href*='cabinet']")
    PHONE_INPUT = (By.CSS_SELECTOR, "input[type='tel'], input[name*='phone']")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    PASSWORD_CHANGE_LINK = (By.XPATH, "//a[contains(., 'unutmusunuz') or contains(., 'Forgot')]")
    OTP_INDICATOR = (By.CSS_SELECTOR, "input[name*='otp'], input[id*='otp']")

    def open_home_page(self) -> None:
        self.open(self.BASE_URL)

    def click_login_button(self) -> bool:
        if not self.click(self.LOGIN_LINK):
            return False
        
        # Quick check for new window
        try:
            WebDriverWait(self.driver, 1).until(lambda d: len(d.window_handles) > 1)
            self.switch_to_new_window()
        except TimeoutException:
            pass
        
        return True

    def is_on_login_page(self) -> bool:
        try:
            self.wait.until(EC.presence_of_element_located(self.PHONE_INPUT))
            return True
        except TimeoutException:
            return "kabinetim" in self.driver.current_url.lower()

    def enter_phone_number(self, phone: str) -> str:
        el = self.wait.until(EC.visibility_of_element_located(self.PHONE_INPUT))
        el.clear()
        el.send_keys(phone)
        return phone

    def get_phone_input_value(self) -> str | None:
        try:
            el = self.driver.find_element(*self.PHONE_INPUT)
            return el.get_attribute("value") or ""
        except Exception:
            return None

    def submit_phone_number(self) -> bool:
        if self.click(self.SUBMIT_BUTTON):
            return True
        
        try:
            input_el = self.driver.find_element(*self.PHONE_INPUT)
            input_el.send_keys(Keys.ENTER)
            return True
        except Exception:
            return False

    def is_on_otp_page(self) -> bool:
        if "otp" in self.driver.current_url.lower():
            return True
        return bool(self.driver.find_elements(*self.OTP_INDICATOR))

    def click_password_change_link(self) -> bool:
        return self.click(self.PASSWORD_CHANGE_LINK)

    def is_on_password_change_page(self) -> bool:
        url = self.driver.current_url.lower()
        return "password" in url or "reset" in url

    @staticmethod
    def normalize_phone_number(phone: str | None) -> str:
        return normalize_phone_number(phone)