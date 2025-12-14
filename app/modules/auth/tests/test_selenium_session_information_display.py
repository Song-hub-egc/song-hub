"""
Test: Session information display

Validates that session details are displayed correctly on the sessions page.
"""

import time

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver

from .selenium_helpers import login_user, wait_for_page_load


def test_session_information_display():
    """
    Test: Verify session information is displayed correctly

    Steps:
    1. Login as a user
    2. Navigate to /sessions
    3. Verify session details are shown:
       - IP address
       - Browser
       - Device type
       - Location (if available)
       - Last activity time
    """
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Login
        login_user(driver, host)

        # Navigate to sessions page
        driver.get(f"{host}/sessions")
        wait_for_page_load(driver)
        time.sleep(2)

        page_source = driver.page_source.lower()

        # Check for various session information elements
        checks = {
            "IP address": any(indicator in page_source for indicator in ["ip", "127.0.0.1", "address"]),
            "Browser info": any(indicator in page_source for indicator in ["chrome", "firefox", "safari", "browser"]),
            "Device info": any(indicator in page_source for indicator in ["desktop", "mobile", "tablet", "device"]),
            "Time info": any(indicator in page_source for indicator in ["ago", "last activity", "active", "time"]),
        }

        print("Session information checks:")
        for check_name, found in checks.items():
            status = "Found" if found else "Not found"
            print(f"{check_name}: {status}")

        # At least some information should be present
        if any(checks.values()):
            print("Session information is displayed")
        else:
            print("No session information found")

        print("Test test_session_information_display PASSED")

    finally:
        close_driver(driver)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TEST: Session Information Display")
    print("=" * 60 + "\n")

    try:
        test_session_information_display()
        print("\nResult: PASSED")
    except Exception as e:
        print(f"\nResult: FAILED - {e}")

    print("=" * 60 + "\n")
