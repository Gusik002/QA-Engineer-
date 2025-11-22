#!/usr/bin/env python3
import sys
import os
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)


class AzercellAutomation:
    BASE_URL = "https://www.azercell.com/az/"
    TIMEOUT = 15

    def __init__(
        self, phone: str, headless: bool = False, keep_open: bool = False
    ):
        self.phone = phone if phone.startswith("0") else f"0{phone}"
        self.headless = headless
        self.keep_open = keep_open
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None

    def setup_driver(self) -> webdriver.Chrome:
        options = webdriver.ChromeOptions()

        if self.headless:
            options.add_argument("--headless=new")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        try:
            driver = webdriver.Chrome(options=options)
        except WebDriverException:
            print("ChromeDriver not found, attempting to install...")
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

        driver.maximize_window()
        driver.set_page_load_timeout(30)
        return driver

    def find_element_by_multiple_locators(
        self, locators: list[tuple], timeout: int = None
    ):
        timeout = timeout or self.TIMEOUT
        wait = WebDriverWait(self.driver, timeout)

        for by, value in locators:
            try:
                element = wait.until(EC.element_to_be_clickable((by, value)))
                return element
            except TimeoutException:
                continue

        raise NoSuchElementException(
            f"Could not find element with any of the provided locators"
        )

    def navigate_to_login(self):
        print(f"Navigating to {self.BASE_URL}...")
        self.driver.get(self.BASE_URL)

        initial_handles = set(self.driver.window_handles)

        login_locators = [
            (By.XPATH, '//a[contains(@href, "kabinetim.azercell.com")]'),
            (By.CSS_SELECTOR, 'a[href*="kabinetim"]'),
            (By.PARTIAL_LINK_TEXT, "Kabinetim"),
        ]

        print("Looking for login button...")
        login_button = self.find_element_by_multiple_locators(login_locators)
        login_button.click()
        print("Login button clicked")

        time.sleep(2)
        self._switch_to_new_window_if_exists(initial_handles)

    def _switch_to_new_window_if_exists(self, initial_handles: set):
        try:
            WebDriverWait(self.driver, 5).until(
                lambda d: len(d.window_handles) > len(initial_handles)
                or "kabinetim" in d.current_url
            )

            current_handles = set(self.driver.window_handles)
            new_handles = current_handles - initial_handles

            if new_handles:
                self.driver.switch_to.window(new_handles.pop())
                print(f"Switched to new window: {self.driver.current_url}")
        except TimeoutException:
            print("No new window opened, continuing...")

    def enter_phone_number(self):
        print(f"Entering phone number: {self.phone}")

        phone_input_locators = [
            (By.CSS_SELECTOR, "input.az-input-field"),
            (By.XPATH, '//input[contains(@class, "az-input-field")]'),
            (By.CSS_SELECTOR, "input[type='tel']"),
            (By.CSS_SELECTOR, "input[type='text']"),
        ]

        phone_input = self.find_element_by_multiple_locators(
            phone_input_locators
        )
        phone_input.clear()
        time.sleep(0.5)
        phone_input.send_keys(self.phone)
        phone_input.send_keys(Keys.ENTER)
        print("Phone number submitted")

        time.sleep(2)

    def navigate_to_password_change(self):
        print("Looking for password change link...")

        password_change_locators = [
            (By.XPATH, '//a[contains(@href, "password-change")]'),
            (By.PARTIAL_LINK_TEXT, "şifrəni unutmusunuz"),
            (By.CSS_SELECTOR, 'a[href*="password-change"]'),
        ]

        try:
            change_link = self.find_element_by_multiple_locators(
                password_change_locators, timeout=10
            )
            change_link.click()
            print("Password change link clicked")
            time.sleep(2)
        except NoSuchElementException:
            print("Password change link not found or not needed")

    def save_screenshot(self, filename: str = "azercell_screenshot.png"):
        if self.driver:
            path = os.path.join(os.getcwd(), filename)
            self.driver.save_screenshot(path)
            print(f"Screenshot saved: {path}")

    def run(self) -> bool:
        try:
            print("=" * 60)
            print("Starting Azercell Automation")
            print("=" * 60)

            self.driver = self.setup_driver()
            self.wait = WebDriverWait(self.driver, self.TIMEOUT)

            self.navigate_to_login()
            self.enter_phone_number()
            self.navigate_to_password_change()

            print("\n" + "=" * 60)
            print(f"Final URL: {self.driver.current_url}")
            print(
                f"Password change page: "
                f"{'YES' if 'password-change' in self.driver.current_url else 'NO'}"
            )
            print("=" * 60)
            print("\nAutomation completed successfully!")
            print("OTP verification is required - script stopping here.")

            if self.keep_open:
                print("\nBrowser will remain open for manual testing.")
                print("Press Ctrl+C to close...")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\nClosing browser...")

            return True

        except KeyboardInterrupt:
            print("\n\nScript interrupted by user")
            return False

        except Exception as e:
            print(f"\nError occurred: {type(e).__name__}: {e}")
            self.save_screenshot("azercell_error.png")
            return False

        finally:
            if self.driver and not self.keep_open:
                self.driver.quit()
                print("Browser closed")


def main():
    default_phone = "507475560"
    phone = sys.argv[1] if len(sys.argv) > 1 else default_phone
    headless = "--headless" in sys.argv
    keep_open = "--keep-open" in sys.argv

    automation = AzercellAutomation(
        phone=phone, headless=headless, keep_open=keep_open
    )
    success = automation.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()