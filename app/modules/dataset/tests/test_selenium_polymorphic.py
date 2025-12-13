import os
import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver


def wait_for_page_to_load(driver, timeout=10):
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )


def test_uvl_upload_flow(test_database_poblated):
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()

        # 1. Login
        driver.get(f"{host}/login")
        try:
            wait_for_page_to_load(driver)
            email = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "email")))
            email.send_keys("user1@example.com")
        except Exception as e:
            print(f"Login failed. URL: {driver.current_url}")
            print(f"Title: {driver.title}")
            print(f"Source: {driver.page_source}")
            raise e

        driver.find_element(By.NAME, "password").send_keys("1234")
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        # 2. Go to Upload
        driver.get(f"{host}/dataset/upload")
        wait_for_page_to_load(driver)

        # 3. Fill Basic Info
        # 3. Fill Basic Info
        try:
            driver.find_element(By.NAME, "title").send_keys("Selenium UVL Dataset")
        except NoSuchElementException:
            print(f"Failed to find title field. URL: {driver.current_url}")
            raise

        driver.find_element(By.NAME, "desc").send_keys("Description for Selenium Test")
        driver.find_element(By.NAME, "tags").send_keys("selenium,test")

        # 4. Upload UVL File
        file_path = os.path.abspath("app/modules/dataset/uvl_examples/file1.uvl")
        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(file_path)

        # 5. Wait for UVL dynamic form (checking 0_button)
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "0_button")))
        except TimeoutException:
            print(driver.page_source)
            raise AssertionError("UVL file upload failed or Dynamic form not rendered.")

        # 6. Check Disclaimer & Submit
        driver.find_element(By.ID, "agreeCheckbox").click()
        time.sleep(1)  # Let UI update state

        upload_btn = driver.find_element(By.ID, "upload_button")
        if not upload_btn.is_enabled():
            # Fallback if click didn't register
            driver.execute_script("document.getElementById('agreeCheckbox').click();")

        # Submit
        # Scroll to button to ensure visibility
        driver.execute_script("arguments[0].scrollIntoView();", upload_btn)
        upload_btn.click()

        # 7. Wait for Redirect to List
        # We expect a redirect to /dataset/list or similar.
        # Simple wait for now.
        time.sleep(5)
        wait_for_page_to_load(driver)

        # 8. Verify Dataset in List
        assert "Selenium UVL Dataset" in driver.page_source

        # 9. Verify View Page (Polymorphism Check)
        # Click on the dataset link
        driver.find_element(By.PARTIAL_LINK_TEXT, "Selenium UVL Dataset").click()
        wait_for_page_to_load(driver)

        # Check if "UVL models" section is present (Specific to UVLDataset)
        assert "UVL models" in driver.page_source
        assert "file1.uvl" in driver.page_source

        print("Selenium Polymorphic Test Passed!")

    finally:
        close_driver(driver)
