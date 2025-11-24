import logging
import time

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.phone import normalize_phone_number

log = logging.getLogger(__name__)


class AzercellLoginPage(BasePage):
    BASE_URL = "https://www.azercell.com/az/"
    LOGIN_URL = "https://kabinetim.azercell.com/login"

    # More specific login link selector (avoid app store links)
    LOGIN_LINK = (
        By.CSS_SELECTOR,
        "a[href*='kabinetim.azercell.com']:not([href*='app']):not([href*='store']), "
        "a[href*='/cabinet']:not([href*='app']), "
        ".header-login a[href*='kabinetim'], "
        "a.login-btn"
    )
    
    PHONE_INPUT = (
        By.CSS_SELECTOR,
        "input[type='tel'], input[name*='phone'], input[id*='phone'], "
        "input[placeholder*='telefon'], input[placeholder*='nömrə']"
    )
    
    # Fixed: removed invalid :has-text() pseudo-selector
    SUBMIT_BUTTON = (
        By.CSS_SELECTOR,
        "button[type='submit'], button.send-otp, button[class*='submit'], "
        "button.btn-primary, button.login-btn, .login-form button"
    )
    
    PASSWORD_CHANGE_LINK = (
        By.XPATH,
        "//a[contains(translate(., 'ŞİFRƏNI UNUTMUSUNUZ', 'şifrəni unutmusunuz'), 'şifrəni unutmusunuz') "
        "or contains(., 'Forgot password') or contains(., 'password-change') or contains(., 'Şifrəni unudub')]"
    )
    
    OTP_INDICATOR = (
        By.CSS_SELECTOR,
        "input[name*='otp'], input[id*='otp'], input[name*='code'], input[type='text'][maxlength='6']"
    )

    def open_home_page(self) -> None:
        log.info("Opening Azercell home page: %s", self.BASE_URL)
        self.open(self.BASE_URL)
        time.sleep(2)
        self._handle_cookie_banner()

    def open_login_page_directly(self) -> None:
        """Direct navigation to login page (faster and more reliable)."""
        log.info("Opening login page directly: %s", self.LOGIN_URL)
        self.open(self.LOGIN_URL)
        time.sleep(2)
        self._handle_cookie_banner()

    def _handle_cookie_banner(self) -> None:
        """Accept cookie banners if present."""
        cookie_selectors = [
            (By.CSS_SELECTOR, "button.cookie-accept"),
            (By.CSS_SELECTOR, "button[id*='cookie']"),
            (By.CSS_SELECTOR, ".cc-dismiss"),
            (By.XPATH, "//button[contains(., 'Qəbul') or contains(., 'Accept') or contains(., 'Razıyam')]"),
        ]
        
        for selector in cookie_selectors:
            try:
                btn = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable(selector)
                )
                btn.click()
                log.info("Cookie banner accepted")
                time.sleep(0.5)
                return
            except TimeoutException:
                continue

    def click_login_button(self) -> bool:
        """
        Click login button/link from homepage.
        Returns True on success, False otherwise.
        """
        log.info("Attempting to click login button")
        
        # Strategy 1: Try to find the correct login link
        if self._try_click_login_link():
            return self._verify_login_page_reached()
        
        # Strategy 2: Direct navigation fallback
        log.warning("Login link click failed, using direct navigation")
        self.open_login_page_directly()
        return self._verify_login_page_reached()

    def _try_click_login_link(self) -> bool:
        """Try to find and click the web login link (not app store link)."""
        try:
            # Wait for page to be ready
            WebDriverWait(self.driver, 5).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Find all links that might be login links
            login_link = None
            try:
                # Try primary selector first
                login_link = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located(self.LOGIN_LINK)
                )
                href = login_link.get_attribute("href") or ""
                log.info("Found login link: %s", href)
                
                # Reject if it's an app store link
                if "app" in href.lower() or "store" in href.lower():
                    log.warning("Found app store link, looking for web login instead")
                    login_link = None
            except TimeoutException:
                log.debug("Primary login selector not found")
            
            # Fallback: find any link with 'kabinetim' that's not an app link
            if not login_link:
                try:
                    all_links = self.driver.find_elements(By.TAG_NAME, "a")
                    for link in all_links:
                        href = link.get_attribute("href") or ""
                        if "kabinetim.azercell.com" in href and "app" not in href.lower():
                            login_link = link
                            log.info("Found web login link via fallback: %s", href)
                            break
                except Exception as e:
                    log.debug("Fallback link search failed: %s", e)
            
            if not login_link:
                log.error("Could not find valid web login link")
                return False
            
            # Store window handles before click
            initial_handles = self.driver.window_handles
            
            # Scroll into view
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});",
                login_link
            )
            time.sleep(0.5)
            
            # Try to click
            try:
                login_link.click()
                log.info("Clicked login link")
            except Exception as e:
                log.warning("Normal click failed (%s), trying JS click", e)
                self.driver.execute_script("arguments[0].click();", login_link)
            
            time.sleep(2)
            
            # Check for new window
            try:
                WebDriverWait(self.driver, 2).until(
                    lambda d: len(d.window_handles) > len(initial_handles)
                )
                log.info("New window opened, switching")
                self.switch_to_new_window()
            except TimeoutException:
                log.debug("No new window")
            
            return True
            
        except Exception as e:
            log.exception("Error clicking login link: %s", e)
            return False

    def _verify_login_page_reached(self) -> bool:
        """Verify we reached the login page."""
        time.sleep(2)
        
        current_url = self.driver.current_url.lower()
        log.info("Current URL: %s", current_url)
        
        # Check URL
        if "kabinetim" in current_url or "login" in current_url:
            log.info("Login page URL confirmed")
            return True
        
        # Check for phone input as fallback
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(self.PHONE_INPUT)
            )
            log.info("Phone input found - on login page")
            return True
        except TimeoutException:
            log.error("Failed to verify login page")
            return False

    def is_on_login_page(self) -> bool:
        """Check if currently on the login page."""
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(self.PHONE_INPUT)
            )
            log.debug("Phone input found - on login page")
            return True
        except TimeoutException:
            current_url = self.driver.current_url.lower()
            is_login = "kabinetim" in current_url or "login" in current_url
            log.debug("Login page check by URL: %s (url=%s)", is_login, current_url)
            return is_login

    def enter_phone_number(self, phone: str) -> str:
        """Enter phone number in input field."""
        log.info("Entering phone number")
        phone = str(phone)
        
        el = self.wait.until(EC.visibility_of_element_located(self.PHONE_INPUT))
        el.clear()
        time.sleep(0.3)
        el.send_keys(phone)
        time.sleep(0.5)
        
        log.info("Phone number entered")
        return phone

    def get_phone_input_value(self) -> str | None:
        """Get current value from phone input."""
        try:
            el = self.driver.find_element(*self.PHONE_INPUT)
            return el.get_attribute("value") or ""
        except Exception as e:
            log.warning("Could not get phone input value: %s", e)
            return None

    def submit_phone_number(self) -> bool:
        """Submit the phone number form."""
        log.info("Submitting phone number")
        
        # Try to click submit button
        try:
            # First, try to find the button
            submit_btn = None
            try:
                submit_btn = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located(self.SUBMIT_BUTTON)
                )
                log.info("Found submit button: %s", submit_btn.get_attribute("class"))
            except TimeoutException:
                log.info("Submit button not found with primary selector")
            
            # If found, try to click it
            if submit_btn:
                try:
                    # Scroll into view and click
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});",
                        submit_btn
                    )
                    time.sleep(0.3)
                    submit_btn.click()
                    log.info("Submit button clicked")
                    time.sleep(2)
                    return True
                except Exception as e:
                    log.warning("Click failed (%s), trying JS click", e)
                    try:
                        self.driver.execute_script("arguments[0].click();", submit_btn)
                        log.info("JS click succeeded")
                        time.sleep(2)
                        return True
                    except Exception as e2:
                        log.warning("JS click also failed: %s", e2)
        
        except Exception as e:
            log.warning("Exception finding submit button: %s", e)
        
        # Fallback: press Enter in phone input
        log.info("Trying Enter key fallback")
        try:
            input_el = self.driver.find_element(*self.PHONE_INPUT)
            input_el.send_keys(Keys.ENTER)
            time.sleep(2)
            log.info("Enter key pressed")
            return True
        except Exception as e:
            log.error("Enter key fallback failed: %s", e)
            return False

    def is_on_otp_page(self) -> bool:
        """Check if on OTP verification page."""
        if "otp" in self.driver.current_url.lower():
            return True
        return bool(self.driver.find_elements(*self.OTP_INDICATOR))

    def click_password_change_link(self) -> bool:
        """Click password change/forgot password link."""
        log.info("Clicking password change link")
        return self.click(self.PASSWORD_CHANGE_LINK)

    def is_on_password_change_page(self) -> bool:
        """Check if on password change page."""
        url = self.driver.current_url.lower()
        return "password" in url or "reset" in url or "sifrə" in url

    @staticmethod
    def normalize_phone_number(phone: str | None) -> str:
        return normalize_phone_number(phone)