from locust import HttpUser, between, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token


class SessionCreationBehavior(HttpUser):
    wait_time = between(1, 3)
    host = get_host_for_locust_testing()

    @task
    def create_multiple_sessions(self):
        """
        Simulate creating multiple sessions by logging in repeatedly.
        Tests the system's ability to handle concurrent session creation.
        """
        # Logout first to ensure clean state
        self.client.get("/logout")

        # Login to create a new session
        response = self.client.get("/login")
        csrf_token = get_csrf_token(response)

        email = "user1@example.com"
        password = "1234"

        with self.client.post(
            "/login",
            data={"email": email, "password": password, "csrf_token": csrf_token},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 302:
                # Redirect is also acceptable
                response.success()
            else:
                response.failure(f"Login failed: {response.status_code}")

        # Verify session was created by accessing sessions page
        with self.client.get("/sessions", catch_response=True) as response:
            if response.status_code == 200:
                if "session" in response.text.lower():
                    response.success()
                else:
                    response.failure("Sessions page did not show session info")
            else:
                response.failure(f"Failed to access sessions: {response.status_code}")


if __name__ == "__main__":
    import os

    os.system(f"locust -f {__file__} --host={get_host_for_locust_testing()}")
