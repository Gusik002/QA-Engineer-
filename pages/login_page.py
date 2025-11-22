from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AzercellLoginPage:
    HOME_URL = "https://www.azercell.com/az/"
    LOGIN_LINK = (By.CSS_SELECTOR,
                  'a.top-bar__block[href*="kabinetim"]')
    PHONE_INPUT = (By.CSS_SELECTOR, "input.az-input-field")
    PASSWORD_CHANGE_LINK = (By.CSS_SELECTOR,
                            'a[href*="password-change"]')

    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self):
        self.driver.get(self.HOME_URL)

    def go_to_login(self):
        self.wait.until(EC.element_to_be_clickable(self.LOGIN_LINK)).click()
        # wait until the phone input appears on the login page
        self.wait.until(EC.visibility_of_element_located(self.PHONE_INPUT))

    def submit_phone(self, phone):
        el = self.wait.until(EC.visibility_of_element_located(self.PHONE_INPUT))
        el.clear()
        el.send_keys(phone)
        # prefer clicking a submit button if present; ENTER is often ok
        el.send_keys(Keys.ENTER)
        # wait for next page or an URL change that indicates submission
        try:
            self.wait.until(EC.url_contains("password-change"))
        except TimeoutException:
            # not fatal here — caller can handle or add a different wait
            pass

    def click_password_change(self):
        self.wait.until(EC.element_to_be_clickable(
            self.PASSWORD_CHANGE_LINK)).click()
        self.wait.until(EC.url_contains("password-change"))

    def is_login_link_present(self, timeout=1):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.LOGIN_LINK)
            )
            return True
        except TimeoutException:
            return False

    def on_password_change_page(self):
        return "password-change" in (self.driver.current_url or "")