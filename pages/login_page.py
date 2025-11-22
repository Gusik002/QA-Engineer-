from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AzercellLoginPage:
    HOME_URL = "https://www.azercell.com/az/"
    LOGIN_LINK = (By.CSS_SELECTOR, 'a.top-bar__block[href*="kabinetim"]')
    PHONE_INPUT = (By.CSS_SELECTOR, "input.az-input-field")
    PASSWORD_CHANGE_LINK = (
        By.CSS_SELECTOR,
        'a[href="/login/password-change/confirm-number"]'
    )

    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self):
        self.driver.get(self.HOME_URL)

    def go_to_login(self):
        self.wait.until(EC.element_to_be_clickable(self.LOGIN_LINK)).click()

    def submit_phone(self, phone):
        el = self.wait.until(EC.element_to_be_clickable(self.PHONE_INPUT))
        el.clear()
        el.send_keys(phone)
        el.send_keys(Keys.ENTER)

    def click_password_change(self):
        self.wait.until(
            EC.element_to_be_clickable(self.PASSWORD_CHANGE_LINK)
        ).click()

    def is_login_link_present(self):
        try:
            self.wait.until(EC.presence_of_element_located(self.LOGIN_LINK))
            return True
        except Exception:
            return False

    def on_password_change_page(self):
        return "password-change" in self.driver.current_url
