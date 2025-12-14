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


def test_image_dataset_upload_flow(test_database_poblated):
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()

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

        driver.get(f"{host}/dataset/upload/image_dataset")
        wait_for_page_to_load(driver)
        time.sleep(2)

        try:
            title_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "title")))
            title_field.send_keys("Selenium Image Dataset")
        except NoSuchElementException:
            print(f"Failed to find title field. URL: {driver.current_url}")
            raise

        driver.find_element(By.NAME, "desc").send_keys("Description for Selenium Image Dataset Test")
        driver.find_element(By.NAME, "tags").send_keys("selenium,image,test")

        image_path = os.path.abspath("app/static/img/icons/icon-250x250.png")

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Test image not found at {image_path}")

        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(image_path)
        wait_for_page_to_load(driver)
        time.sleep(3)  # Additional wait for Dropzone to process the file

        try:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "0_button")))
        except TimeoutException:
            print(f"Failed to find 0_button. URL: {driver.current_url}")
            try:
                alerts = driver.find_element(By.ID, "alerts")
                if alerts.is_displayed():
                    print(f"Alerts found: {alerts.text}")
            except NoSuchElementException:
                print("No #alerts element found")

            try:
                logs = driver.get_log("browser")
                print("Browser logs:")
                for log in logs:
                    print(log)
            except Exception:
                print("Could not retrieve browser logs")

            raise AssertionError("Image file upload failed or Dynamic form not rendered.")

        agree_checkbox = driver.find_element(By.ID, "agreeCheckbox")
        driver.execute_script("arguments[0].click();", agree_checkbox)
        time.sleep(1)  # Let UI update state

        upload_btn = driver.find_element(By.ID, "upload_button")
        if not upload_btn.is_enabled():
            driver.execute_script("document.getElementById('agreeCheckbox').click();")

        driver.execute_script("arguments[0].scrollIntoView();", upload_btn)
        driver.execute_script("arguments[0].click();", upload_btn)

        time.sleep(5)
        wait_for_page_to_load(driver)

        assert "Selenium Image Dataset" in driver.page_source

        link = driver.find_element(By.PARTIAL_LINK_TEXT, "Selenium Image Dataset")
        driver.execute_script("arguments[0].click();", link)
        wait_for_page_to_load(driver)

        assert "Images" in driver.page_source
        assert "icon-250x250.png" in driver.page_source

        print("Selenium Image Dataset Test Passed!")

    finally:
        if os.path.exists("app/modules/imagedataset/tests/test_image.png"):
            os.remove("app/modules/imagedataset/tests/test_image.png")
        close_driver(driver)
