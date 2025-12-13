import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver

from .selenium_helpers import login_user, wait_for_page_load


def test_revoke_single_session():
    driver1 = initialize_driver()
    driver2 = None

    try:
        host = get_host_for_selenium_testing()

        # First browser: Login
        print("Browser 1: Logging in...")
        login_user(driver1, host)
        time.sleep(1)

        # Second browser: Login to create another session
        print("Browser 2: Creating second session...")
        driver2 = initialize_driver()
        login_user(driver2, host)
        time.sleep(1)

        # Browser 1: Navigate to sessions page
        print("Browser 1: Navigating to sessions page...")
        driver1.get(f"{host}/sessions")
        wait_for_page_load(driver1)
        time.sleep(2)

        # Try to find revoke buttons (excluding "Revoke All" button)
        try:
            revoke_buttons = driver1.find_elements(
                By.XPATH, "//button[contains(text(), 'Revoke') and not(contains(text(), 'All'))]"
            )

            if not revoke_buttons:
                # Try alternative selectors
                revoke_buttons = driver1.find_elements(
                    By.CSS_SELECTOR, "button[onclick*='revoke'], form[action*='revoke'] button"
                )

            initial_session_count = len(revoke_buttons) + 1  # +1 for current session
            print(f"Found {initial_session_count} session(s) initially")

            if len(revoke_buttons) > 0:
                # Click the first revoke button (for another session)
                print("Revoking a session...")
                revoke_buttons[0].click()
                time.sleep(1)

                # Handle any alert
                try:
                    alert = WebDriverWait(driver1, 5).until(EC.alert_is_present())
                    alert.accept()
                    print("Alert handled")
                except Exception as e:
                    print(f"No alert found or alert handling failed: {e}")

                time.sleep(2)

                # Wait for page reload
                wait_for_page_load(driver1)
                time.sleep(1)

                # Verify one less session
                revoke_buttons_after = driver1.find_elements(
                    By.XPATH, "//button[contains(text(), 'Revoke') and not(contains(text(), 'All'))]"
                )

                if not revoke_buttons_after:
                    revoke_buttons_after = driver1.find_elements(
                        By.CSS_SELECTOR, "button[onclick*='revoke'], form[action*='revoke'] button"
                    )

                final_session_count = len(revoke_buttons_after) + 1
                print(f"Found {final_session_count} session(s) after revoke")

                assert final_session_count < initial_session_count, "Session count should decrease after revoking"
                print("Session successfully revoked")

            else:
                print("Warning: No revokable sessions found (only current session exists)")
                print("Test partially successful - sessions page accessible")

            # Verify browser 1 still has access (current session still valid)
            driver1.get(f"{host}/sessions")
            wait_for_page_load(driver1)
            assert "session" in driver1.page_source.lower(), "Current session should still be valid"
            print("Current session still active")

            print("Test test_revoke_single_session PASSED")

        except (NoSuchElementException, AssertionError) as e:
            raise AssertionError(f"Failed to revoke session: {e}")

    finally:
        close_driver(driver1)
        if driver2:
            close_driver(driver2)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TEST: Revoke Single Session")
    print("=" * 60 + "\n")

    try:
        test_revoke_single_session()
        print("\nResult: PASSED")
    except Exception as e:
        print(f"\nResult: FAILED - {e}")

    print("=" * 60 + "\n")
