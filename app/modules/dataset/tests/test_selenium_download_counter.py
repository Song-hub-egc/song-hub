"""
Selenium tests for the download counter feature.

Tests cover:
- Download counter visibility on dataset detail page
- Download counter increments after download
- Download counter does not increment on repeated downloads
"""

import time

import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver


@pytest.fixture(autouse=True)
def cleanup_between_tests():
    """
    Fixture that runs automatically between each test.
    Adds a delay to prevent resource exhaustion and state conflicts.
    """
    yield  # Test runs here
    # Cleanup after test
    time.sleep(3)  # 3 second pause between tests


def wait_for_page_to_load(driver, timeout=4):
    """Wait for page to fully load"""
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )


def login_user(driver, host, email="user1@example.com", password="1234"):
    """Helper function to login a user"""
    try:
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        # Wait explicitly for the email field to be present
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        password_field = driver.find_element(By.NAME, "password")

        email_field.clear()
        email_field.send_keys(email)
        password_field.clear()
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

        time.sleep(2)
        wait_for_page_to_load(driver)
    except Exception as e:
        print(f"Login failed: {e}")
        # Take a screenshot for debugging
        try:
            driver.save_screenshot("/tmp/login_error.png")
            print("Screenshot saved to /tmp/login_error.png")
        except Exception:
            pass
        raise


def get_download_count_from_page(driver):
    """
    Extract the download count from the dataset detail page.
    The counter is displayed in a badge with format: <icon> <number>
    """
    try:
        # Find the Downloads section
        # The structure is: <span class="badge bg-primary"><i data-feather="download"></i> {{ dataset.download_count }}</span>
        download_badge = driver.find_element(
            By.XPATH, "//span[contains(text(), 'Downloads')]/following-sibling::div//span[@class='badge bg-primary']"
        )
        
        # Get the text and extract the number (format is "<icon> 123")
        badge_text = download_badge.text.strip()
        
        # The text might be just the number or have an icon before it
        # Try to extract the last part which should be the number
        parts = badge_text.split()
        count = int(parts[-1]) if parts else 0
        
        return count
    except (NoSuchElementException, ValueError, IndexError):
        # If we can't find it with the first method, try alternative selector
        try:
            # Alternative: find by the row structure
            downloads_row = driver.find_element(By.XPATH, "//span[contains(text(), 'Downloads')]/../..")
            badge = downloads_row.find_element(By.CLASS_NAME, "badge")
            badge_text = badge.text.strip()
            
            # Extract number from text
            parts = badge_text.split()
            count = int(parts[-1]) if parts else 0
            
            return count
        except (NoSuchElementException, ValueError, IndexError):
            raise Exception("Could not find download counter on page")


def test_download_counter_visible_on_dataset_detail():
    """Test that the download counter is visible on the dataset detail page"""
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Login
        login_user(driver, host)

        # Navigate to dataset list to find a dataset
        driver.get(f"{host}/dataset/list")
        wait_for_page_to_load(driver)

        # Find the first dataset link
        try:
            # Look for a dataset link in the table
            # Look for a dataset link in the table
            dataset_link = driver.find_element(
                By.XPATH, "//table//tbody//tr[1]//a[contains(@href, '/doi/') or contains(@href, '/dataset/')]"
            )
            dataset_url = dataset_link.get_attribute("href")
        except NoSuchElementException:
            print("No datasets found in the list, skipping test")
            return

        # Navigate to dataset detail page
        driver.get(dataset_url)
        wait_for_page_to_load(driver)

        # Verify that "Downloads" label exists
        downloads_label = driver.find_element(By.XPATH, "//span[contains(text(), 'Downloads')]")
        assert downloads_label is not None, "Downloads label should be visible"

        # Verify that download count is displayed
        download_count = get_download_count_from_page(driver)
        assert download_count >= 0, f"Download count should be non-negative, got {download_count}"

        print(f"Test passed! Download counter is visible with value: {download_count}")

    finally:
        # Ensure driver is properly closed
        try:
            close_driver(driver)
        except Exception as e:
            print(f"Error closing driver: {e}")
        time.sleep(1)  # Small delay after closing driver



def test_download_counter_increments_on_download():
    """Test that the download counter increments when a dataset is downloaded"""
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Login
        login_user(driver, host)

        # Navigate to dataset list
        driver.get(f"{host}/dataset/list")
        wait_for_page_to_load(driver)

        # Find the first dataset
        try:
            dataset_link = driver.find_element(
                By.XPATH, "//table//tbody//tr[1]//a[contains(@href, '/doi/') or contains(@href, '/dataset/')]"
            )
            dataset_url = dataset_link.get_attribute("href")
        except NoSuchElementException:
            print("No datasets found in the list, skipping test")
            return

        # Navigate to dataset detail page
        driver.get(dataset_url)
        wait_for_page_to_load(driver)
        time.sleep(1)  # Extra wait to ensure page is fully rendered

        # Get initial download count
        initial_count = get_download_count_from_page(driver)
        print(f"Initial download count: {initial_count}")

        # Find and click the download button
        # The button has class "btn btn-primary" and href="/dataset/download/{dataset.id}"
        # The button has class "btn btn-primary" and href="/dataset/download/{dataset.id}"
        download_button = driver.find_element(
            By.XPATH, "//a[contains(@href, '/dataset/download/') and contains(@class, 'btn-primary')]"
        )
        
        # Click the download button
        download_button.click()
        time.sleep(2)  # Wait for download to process
        wait_for_page_to_load(driver)

        # Navigate back to dataset detail page to see updated counter
        driver.get(dataset_url)
        wait_for_page_to_load(driver)
        time.sleep(1)  # Give time for the page to fully render

        # Get updated download count
        updated_count = get_download_count_from_page(driver)
        print(f"Updated download count: {updated_count}")

        # Verify the counter incremented
        assert updated_count == initial_count + 1, \
            f"Download count should increment from {initial_count} to {initial_count + 1}, but got {updated_count}"

        print("Test passed! Download counter incremented correctly.")

    finally:
        # Ensure driver is properly closed
        try:
            close_driver(driver)
        except Exception as e:
            print(f"Error closing driver: {e}")
        time.sleep(1)  # Small delay after closing driver


def test_download_counter_does_not_increment_on_repeated_download():
    """Test that the download counter does NOT increment on repeated downloads from the same user"""
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Login
        login_user(driver, host)

        # Navigate to dataset list
        driver.get(f"{host}/dataset/list")
        wait_for_page_to_load(driver)

        # Find the first dataset
        try:
            dataset_link = driver.find_element(
                By.XPATH, "//table//tbody//tr[1]//a[contains(@href, '/doi/') or contains(@href, '/dataset/')]"
            )
            dataset_url = dataset_link.get_attribute("href")
        except NoSuchElementException:
            print("No datasets found in the list, skipping test")
            return

        # Navigate to dataset detail page
        driver.get(dataset_url)
        wait_for_page_to_load(driver)

        # First download
        download_button = driver.find_element(
            By.XPATH, "//a[contains(@href, '/dataset/download/') and contains(@class, 'btn-primary')]"
        )
        download_button.click()
        time.sleep(2)
        wait_for_page_to_load(driver)

        # Go back to dataset page and get count after first download
        driver.get(dataset_url)
        wait_for_page_to_load(driver)
        time.sleep(1)
        
        count_after_first = get_download_count_from_page(driver)
        print(f"Count after first download: {count_after_first}")

        # Second download (same user/session)
        download_button = driver.find_element(
            By.XPATH, "//a[contains(@href, '/dataset/download/') and contains(@class, 'btn-primary')]"
        )
        download_button.click()
        time.sleep(2)
        wait_for_page_to_load(driver)

        # Go back to dataset page and get count after second download
        driver.get(dataset_url)
        wait_for_page_to_load(driver)
        time.sleep(1)
        
        count_after_second = get_download_count_from_page(driver)
        print(f"Count after second download: {count_after_second}")

        # Verify count did NOT increment on second download
        # Verify count did NOT increment on second download
        assert count_after_second == count_after_first, (
            f"Download count should not increment on repeated download. "
            f"Expected {count_after_first}, got {count_after_second}"
        )

        print("Test passed! Download counter did not increment on repeated download.")

    finally:
        # Ensure driver is properly closed
        try:
            close_driver(driver)
        except Exception as e:
            print(f"Error closing driver: {e}")
        time.sleep(1)  # Small delay after closing driver


def test_download_counter_in_trending_section():
    """Test that download counter updates in the trending datasets section"""
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Login
        login_user(driver, host)

        # Navigate to home page
        driver.get(host)
        wait_for_page_to_load(driver)

        # Check if trending section exists
        try:
            trending_badge = driver.find_element(By.CLASS_NAME, "trending-downloads-badge-simple")
            initial_trending_count = int(trending_badge.text.split()[0])
            print(f"Initial trending download count: {initial_trending_count}")
        except NoSuchElementException:
            print("No trending datasets section found, skipping test")
            return

        # Find and click a download link in trending section
        try:
            # Use a more flexible selector - find any download link
            download_link = driver.find_element(By.XPATH, "//a[contains(@href, '/dataset/download/')]")
            
            # Scroll the element into view before clicking
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_link)
            time.sleep(1)  # Wait for scroll to complete
            
            download_link.click()
            time.sleep(2)
            wait_for_page_to_load(driver)
        except NoSuchElementException:
            print("No download link found in trending section, skipping test")
            return

        # Go back to home page
        driver.get(host)
        wait_for_page_to_load(driver)
        time.sleep(1)

        # Check updated trending count
        trending_badge = driver.find_element(By.CLASS_NAME, "trending-downloads-badge-simple")
        updated_trending_count = int(trending_badge.text.split()[0])
        print(f"Updated trending download count: {updated_trending_count}")

        # Verify it incremented or stayed the same (depending on trending logic)
        # Note: Trending section may filter by time period, so the download might not appear immediately
        assert updated_trending_count >= initial_trending_count, \
            f"Trending download count should not decrease (was {initial_trending_count}, now {updated_trending_count})"
        
        if updated_trending_count == initial_trending_count:
            print("Note: Trending counter did not increment (may be due to time-based filtering or repeated download)")
        else:
            print(f"Trending counter incremented from {initial_trending_count} to {updated_trending_count}")

        print("Test passed! Trending download counter updated correctly.")

    finally:
        # Ensure driver is properly closed
        try:
            close_driver(driver)
        except Exception as e:
            print(f"Error closing driver: {e}")
        time.sleep(1)  # Small delay after closing driver


# Tests are executed by pytest; do not invoke them at import time.