from locust import HttpUser, between, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token


class SessionViewBehavior(HttpUser):
    wait_time = between(1, 3)
    host = get_host_for_locust_testing()

    def on_start(self):
        """Login before starting tasks"""
        self.login()

    def login(self):
        """Login with test credentials"""
        response = self.client.get("/login")
        csrf_token = get_csrf_token(response)

        response = self.client.post(
            "/login",
            data={"email": "user1@example.com", "password": "1234", "csrf_token": csrf_token},
            allow_redirects=True,
        )

        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")

    @task(3)
    def view_sessions(self):
        """View active sessions page - most common operation"""
        with self.client.get("/sessions", catch_response=True) as response:
            if response.status_code == 200:
                if "session" in response.text.lower():
                    response.success()
                else:
                    response.failure("Sessions page did not contain expected content")
            elif response.status_code == 302:
                # Redirect might be expected behavior
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(1)
    def view_sessions_and_check_details(self):
        """View sessions and verify session details are present"""
        with self.client.get("/sessions", catch_response=True) as response:
            if response.status_code == 200:
                content = response.text.lower()
                # Check for session information elements
                has_info = any(keyword in content for keyword in ["ip", "browser", "device", "active"])
                if has_info:
                    response.success()
                else:
                    response.failure("Session details not found in response")
            else:
                response.failure(f"Failed to load sessions: {response.status_code}")


if __name__ == "__main__":
    import os

    os.system(f"locust -f {__file__} --host={get_host_for_locust_testing()}")
