import pytest

from core.selenium.common import close_driver, initialize_driver


@pytest.fixture(scope="module")
def driver():
    driver = initialize_driver()
    yield driver
    close_driver(driver)
