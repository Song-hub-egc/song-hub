"""
Common helper functions for session management Selenium tests.
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait


def wait_for_page_load(driver, timeout=10):
    """Wait for page to load completely."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def login_user(driver, host, email="user1@example.com", password="1234"):
    """Helper function to login a user."""
    driver.get(f"{host}/login")
    wait_for_page_load(driver)
    
    email_field = driver.find_element(By.NAME, "email")
    password_field = driver.find_element(By.NAME, "password")
    
    email_field.clear()
    email_field.send_keys(email)
    password_field.clear()
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
    
    # Wait for redirect after login
    time.sleep(3)
    wait_for_page_load(driver)


def logout_user(driver, host):
    """Helper function to logout a user."""
    driver.get(f"{host}/logout")
    wait_for_page_load(driver)
