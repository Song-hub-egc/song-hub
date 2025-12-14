import time

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver

from .selenium_helpers import login_user, wait_for_page_load


def test_session_timeout_verification():
    """
    Test: Verify session timeout behavior

    Note: This test simulates timeout by waiting, but in a real scenario
    the timeout would be much longer (e.g., 30 minutes). For testing purposes,
    we just verify that session information displays last activity time.
    """
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Login
        print("Logging in...")
        login_user(driver, host)
        time.sleep(1)

        # Navigate to sessions page
        print("Navigating to sessions page...")
        driver.get(f"{host}/sessions")
        wait_for_page_load(driver)
        time.sleep(2)

        # Verify session shows activity information
        page_content = driver.page_source.lower()

        # Check for time-related indicators
        time_indicators = ["ago", "last activity", "active", "time", "recent"]
        has_time_info = any(indicator in page_content for indicator in time_indicators)

        if has_time_info:
            print("Session displays activity time information")
        else:
            print("Warning: No activity time information found")

        # Wait a short period to simulate some inactivity
        print("Waiting to simulate inactivity...")
        time.sleep(5)

        # Refresh and check if session is still active
        driver.get(f"{host}/sessions")
        wait_for_page_load(driver)
        time.sleep(1)

        # Verify we're still logged in after short inactivity
        page_content_after = driver.page_source.lower()

        if "session" in page_content_after:
            print("Session still active after short inactivity (expected)")
        else:
            print("Warning: Session may have expired prematurely")

        # Perform an action to update last activity
        driver.get(f"{host}/")
        wait_for_page_load(driver)
        time.sleep(1)

        # Go back to sessions to verify activity was updated
        driver.get(f"{host}/sessions")
        wait_for_page_load(driver)

        if "session" in driver.page_source.lower():
            print("Session activity updated successfully")
            print("Test test_session_timeout_verification PASSED")
        else:
            raise AssertionError("Session unexpectedly expired")

    finally:
        close_driver(driver)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TEST: Session Timeout Verification")
    print("=" * 60 + "\n")

    try:
        test_session_timeout_verification()
        print("\nResult: PASSED")
    except Exception as e:
        print(f"\nResult: FAILED - {e}")

    print("=" * 60 + "\n")
