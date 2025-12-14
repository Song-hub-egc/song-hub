import os
import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver


def wait_for_page_to_load(driver, timeout=4):
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )


def count_datasets(driver, host):
    driver.get(f"{host}/dataset/list")
    wait_for_page_to_load(driver)

    try:
        amount_datasets = len(driver.find_elements(By.XPATH, "//table//tbody//tr"))
    except Exception:
        amount_datasets = 0
    return amount_datasets


def test_upload_dataset():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")

        password_field.send_keys(Keys.RETURN)
        time.sleep(4)
        wait_for_page_to_load(driver)

        initial_datasets = count_datasets(driver, host)

        driver.get(f"{host}/dataset/upload")
        wait_for_page_to_load(driver)

        title_field = driver.find_element(By.NAME, "title")
        title_field.send_keys("Title")
        desc_field = driver.find_element(By.NAME, "desc")
        desc_field.send_keys("Description")
        tags_field = driver.find_element(By.NAME, "tags")
        tags_field.send_keys("tag1,tag2")

        add_author_button = driver.find_element(By.ID, "add_author")
        driver.execute_script("arguments[0].click();", add_author_button)
        wait_for_page_to_load(driver)
        driver.execute_script("arguments[0].click();", add_author_button)
        wait_for_page_to_load(driver)

        name_field0 = driver.find_element(By.NAME, "authors-0-name")
        name_field0.send_keys("Author0")
        affiliation_field0 = driver.find_element(By.NAME, "authors-0-affiliation")
        affiliation_field0.send_keys("Club0")
        orcid_field0 = driver.find_element(By.NAME, "authors-0-orcid")
        orcid_field0.send_keys("0000-0000-0000-0000")

        name_field1 = driver.find_element(By.NAME, "authors-1-name")
        name_field1.send_keys("Author1")
        affiliation_field1 = driver.find_element(By.NAME, "authors-1-affiliation")
        affiliation_field1.send_keys("Club1")

        file1_path = os.path.abspath("app/modules/dataset/uvl_examples/file1.uvl")
        file2_path = os.path.abspath("app/modules/dataset/uvl_examples/file2.uvl")

        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(file1_path)
        wait_for_page_to_load(driver)

        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(file2_path)
        wait_for_page_to_load(driver)

        try:
            show_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "0_button")))
            driver.execute_script("arguments[0].click();", show_button)

            add_author_uvl_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "0_form_authors_button"))
            )
            driver.execute_script("arguments[0].click();", add_author_uvl_button)
            wait_for_page_to_load(driver)
        except TimeoutException:
            # Make the failure clearer in test output
            raise NoSuchElementException("Could not find UVL model buttons (0_button / 0_form_authors_button)")

        name_field = driver.find_element(By.NAME, "feature_models-0-authors-2-name")
        name_field.send_keys("Author3")
        affiliation_field = driver.find_element(By.NAME, "feature_models-0-authors-2-affiliation")
        affiliation_field.send_keys("Club3")

        check = driver.find_element(By.ID, "agreeCheckbox")
        driver.execute_script("arguments[0].click();", check)
        wait_for_page_to_load(driver)

        upload_btn = driver.find_element(By.ID, "upload_button")
        driver.execute_script("arguments[0].scrollIntoView();", upload_btn)
        driver.execute_script("arguments[0].click();", upload_btn)
        wait_for_page_to_load(driver)

        final_datasets = None
        deadline = time.time() + 10
        while time.time() < deadline:
            try:
                final_datasets = count_datasets(driver, host)
                if final_datasets == initial_datasets + 1:
                    break
            except Exception:
                pass
            time.sleep(0.5)

        if final_datasets != initial_datasets + 1:
            raise AssertionError(
                f"Upload did not result in a new dataset: initial={initial_datasets}, final={final_datasets}"
            )

        print("Test passed!")

    finally:

        close_driver(driver)


def test_trending_datasets():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        driver.get(host)
        driver.set_window_size(1470, 919)
        driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(6) .align-middle:nth-child(2)").click()
        driver.find_element(By.ID, "email").click()
        driver.find_element(By.ID, "email").send_keys("user1@example.com")
        driver.find_element(By.CSS_SELECTOR, ".row:nth-child(4) .mb-3").click()
        driver.find_element(By.ID, "password").click()
        driver.find_element(By.ID, "password").send_keys("1234")
        driver.find_element(By.ID, "submit").click()
        wait_for_page_to_load(driver)
        time.sleep(2)

        try:
            download_element = driver.find_element(By.CSS_SELECTOR, ".trending-downloads-badge-simple")
            initial_download = int(download_element.text.split(" ")[0])
        except NoSuchElementException:
            initial_download = 0

        try:
            download_link = driver.find_element(By.XPATH, "//a[contains(@href, '/dataset/download/')]")
            download_link.click()
        except NoSuchElementException:
            raise AssertionError("No download link found on the trending datasets page")

        time.sleep(2)
        driver.get(host)
        wait_for_page_to_load(driver)

        try:
            updated_downloads = driver.find_element(By.CSS_SELECTOR, ".trending-downloads-badge-simple")
            updated_text = updated_downloads.text.split(" ")[0]
            updated_count = int(updated_text)
            assert (
                updated_count >= initial_download
            ), f"Trending count should not decrease (was {initial_download}, now {updated_count})"
        except NoSuchElementException:
            raise AssertionError("Trending downloads badge not found after download")

        print("Test passed!")

    finally:
        close_driver(driver)
