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

        # 2. Go to Upload Image Dataset
        driver.get(f"{host}/dataset/upload/image_dataset")
        wait_for_page_to_load(driver)
        time.sleep(2)

        # 3. Fill Basic Info
        # 3. Fill Basic Info
        try:
            title_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "title")))
            title_field.send_keys("Selenium Image Dataset")
        except NoSuchElementException:
            print(f"Failed to find title field. URL: {driver.current_url}")
            raise

        driver.find_element(By.NAME, "desc").send_keys("Description for Selenium Image Dataset Test")
        driver.find_element(By.NAME, "tags").send_keys("selenium,image,test")

        # 4. Upload Image File
        # Ensure we have a dummy image.
        # Using a widely available image or creating one?
        # Ideally we should have a fixture, but for now I'll point to a generated one.
        image_path = os.path.abspath("app/modules/imagedataset/tests/test_image.png")
        if not os.path.exists(image_path):
            with open(image_path, "wb") as f:
                f.write(
                    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
                    b"\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00"
                    b"\x00\x00\x00\x00IEND\xaeB`\x82"
                )

        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(image_path)
        wait_for_page_to_load(driver)
        time.sleep(3)  # Additional wait for Dropzone to process the file

        # 5. Wait for dynamic form (checking 0_button)
        try:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "0_button")))
        except TimeoutException:
            print(f"Failed to find 0_button. URL: {driver.current_url}")
            print(f"Page source snippet: {driver.page_source[:500]}")
            raise AssertionError("Image file upload failed or Dynamic form not rendered.")

        # 6. Check Disclaimer & Submit
        # 6. Check Disclaimer & Submit
        driver.find_element(By.ID, "agreeCheckbox").click()
        time.sleep(1)  # Let UI update state

        upload_btn = driver.find_element(By.ID, "upload_button")
        if not upload_btn.is_enabled():
            driver.execute_script("document.getElementById('agreeCheckbox').click();")

        # Submit
        driver.execute_script("arguments[0].scrollIntoView();", upload_btn)
        upload_btn.click()

        # 7. Wait for Redirect to List
        time.sleep(5)
        wait_for_page_to_load(driver)

        # 8. Verify Dataset in List
        assert "Selenium Image Dataset" in driver.page_source

        # 9. Verify View Page (Polymorphism Check)
        driver.find_element(By.PARTIAL_LINK_TEXT, "Selenium Image Dataset").click()
        wait_for_page_to_load(driver)

        # Check if "Images" section is present (Specific to ImageDataset)
        assert "Images" in driver.page_source
        assert "test_image.png" in driver.page_source

        print("Selenium Image Dataset Test Passed!")

    finally:
        if os.path.exists("app/modules/imagedataset/tests/test_image.png"):
            os.remove("app/modules/imagedataset/tests/test_image.png")
        close_driver(driver)
