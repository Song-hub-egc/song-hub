import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver


def wait_for_page_to_load(driver, timeout=4):
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )


def login(driver, host):
    driver.get(f"{host}/login")
    wait_for_page_to_load(driver)
    email_field = driver.find_element(By.NAME, "email")
    password_field = driver.find_element(By.NAME, "password")
    
    email_field.send_keys("user1@example.com")
    password_field.send_keys("1234")
    password_field.send_keys(Keys.RETURN)
    wait_for_page_to_load(driver)


def test_add_to_cart():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()
        login(driver, host)

        # 1. Clear cart first to ensure clean state
        # We can hit the clear endpoint via JS or UI if available, 
        # or just ignore if we only check increment. 
        # But let's try to start fresh if possible.
        # There is a clearCart helper in JS in cart page, but we are not there.
        # We'll just assume we can add.

        # 2. Go to dataset list and pick the first one
        driver.get(f"{host}/dataset/list")
        wait_for_page_to_load(driver)
        
        # Find the first dataset link/button. 
        # Assuming there is at least one dataset (from seeds or manually created).
        # We look for a link that goes to /dataset/<id>
        # Let's try to find a link with "View" or the title.
        try:
             # Try to find a link to a dataset. 
             # Adjust selector based on list_datasets.html structure if known, 
             # but usually there's a title link.
             dataset_link = WebDriverWait(driver, 10).until(
                 EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/dataset/') and not(contains(@href, 'list')) and not(contains(@href, 'upload'))]"))
             )
             dataset_link.click()
             wait_for_page_to_load(driver)
        except Exception:
             print("No datasets found in list. Creating one...")
             # Fallback: Upload a dataset? Or fail? 
             # Ideally we should have data. 
             # Let's assume there is data as per "functionality... implemented" which implies usage.
             # If no data, test fails.
             raise Exception("No datasets found to test with.")
        
        # Get initial cart count if possible (might be hidden if 0)
        try:
            cart_badge = driver.find_element(By.ID, "cart-count")
            initial_count = int(cart_badge.text) if cart_badge.is_displayed() else 0
        except:
            initial_count = 0

        # 4. Click add
        add_btn.click()

        # 5. Verify Success Toast
        # Toast class: alert-success
        toast = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        assert "Added to cart" in toast.text, "Toast message did not match expected text"

        # 6. Verify Cart Count Increased
        # Wait for badge text to change
        WebDriverWait(driver, 10).until(
            lambda d: int(d.find_element(By.ID, "cart-count").text) == initial_count + 1
        )
        
        print("Test passed: Model added to cart successfully.")

    except Exception as e:
        print(f"Test failed with error: {e}")
        try:
            print("Current URL:", driver.current_url)
            print("Page Source at failure:")
            print(driver.page_source)
        except:
            pass
        raise e
    finally:
        close_driver(driver)


if __name__ == "__main__":
    test_add_to_cart()
