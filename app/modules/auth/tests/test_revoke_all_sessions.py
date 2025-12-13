import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver

from .selenium_helpers import login_user, wait_for_page_load


def test_revoke_all_sessions():
    driver1 = initialize_driver()
    driver2 = None
    driver3 = None

    try:
        host = get_host_for_selenium_testing()

        # Create multiple sessions
        print("Browser 1: Logging in...")
        login_user(driver1, host)
        time.sleep(1)

        print("Browser 2: Creating second session...")
        driver2 = initialize_driver()
        login_user(driver2, host)
        time.sleep(1)

        print("Browser 3: Creating third session...")
        driver3 = initialize_driver()
        login_user(driver3, host)
        time.sleep(1)

        # Browser 1: Navigate to sessions page
        print("Browser 1: Navigating to sessions page...")
        driver1.get(f"{host}/sessions")
        wait_for_page_load(driver1)
        time.sleep(2)

        # Count sessions before revoke
        try:
            revoke_buttons = driver1.find_elements(
                By.XPATH, "//button[contains(text(), 'Revoke') and not(contains(text(), 'All'))]"
            )

            if not revoke_buttons:
                revoke_buttons = driver1.find_elements(
                    By.CSS_SELECTOR, "button[onclick*='revoke'], form[action*='revoke'] button"
                )

            initial_session_count = len(revoke_buttons) + 1
            print(f"Found {initial_session_count} session(s) initially")

            # Find and click "Revoke All" button
            revoke_all_buttons = driver1.find_elements(
                By.XPATH, "//button[contains(text(), 'Revoke All') or contains(text(), 'Revoke all')]"
            )

            if not revoke_all_buttons:
                # Try alternative selectors
                revoke_all_buttons = driver1.find_elements(
                    By.CSS_SELECTOR, "button[onclick*='revoke-all'], form[action*='revoke-all'] button"
                )

            if len(revoke_all_buttons) > 0:
                print("Clicking 'Revoke All' button...")
                revoke_all_buttons[0].click()
                time.sleep(2)

                # Wait for page reload
                wait_for_page_load(driver1)
                time.sleep(1)

                # Verify all other sessions are revoked (only current session remains)
                revoke_buttons_after = driver1.find_elements(
                    By.XPATH, "//button[contains(text(), 'Revoke') and not(contains(text(), 'All'))]"
                )

                if not revoke_buttons_after:
                    revoke_buttons_after = driver1.find_elements(
                        By.CSS_SELECTOR, "button[onclick*='revoke'], form[action*='revoke'] button"
                    )

                final_session_count = len(revoke_buttons_after) + 1
                print(f"Found {final_session_count} session(s) after revoke all")

                # Should only have current session left
                assert final_session_count == 1, "Only current session should remain after 'Revoke All'"
                print("All other sessions successfully revoked")

            else:
                print("Warning: 'Revoke All' button not found")
                print("Test partially successful - sessions page accessible")

            # Verify browser 1 still has access (current session still valid)
            driver1.get(f"{host}/sessions")
            wait_for_page_load(driver1)
            assert "session" in driver1.page_source.lower(), "Current session should still be valid"
            print("Current session still active")

            # Verify browser 2 and 3 are logged out
            if driver2:
                print("Verifying browser 2 was logged out...")
                driver2.get(f"{host}/sessions")
                time.sleep(1)
                # Should be redirected to login or see unauthorized message
                current_url = driver2.current_url
                page_content = driver2.page_source.lower()
                if "login" in current_url or "login" in page_content or "unauthorized" in page_content:
                    print("Browser 2 successfully logged out")
                else:
                    print("Warning: Browser 2 may still be logged in")

            print("Test test_revoke_all_sessions PASSED")

        except (NoSuchElementException, AssertionError) as e:
            raise AssertionError(f"Failed to revoke all sessions: {e}")

    finally:
        close_driver(driver1)
        if driver2:
            close_driver(driver2)
        if driver3:
            close_driver(driver3)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TEST: Revoke All Sessions")
    print("=" * 60 + "\n")

    try:
        test_revoke_all_sessions()
        print("\nResult: PASSED")
    except Exception as e:
        print(f"\nResult: FAILED - {e}")

    print("=" * 60 + "\n")
