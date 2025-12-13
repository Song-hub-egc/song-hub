from locust import HttpUser, between, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token


class SessionRevokeBehavior(HttpUser):
    wait_time = between(1, 3)
    host = get_host_for_locust_testing()

    def on_start(self):
        """Login and create a session before starting tasks"""
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

    @task(2)
    def view_sessions_before_revoke(self):
        """View sessions page to see active sessions"""
        with self.client.get("/sessions", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to view sessions: {response.status_code}")

    @task(1)
    def attempt_revoke_all(self):
        """Attempt to revoke all sessions (excluding current)"""
        # First get the sessions page to get CSRF token
        response = self.client.get("/sessions")
        if response.status_code != 200:
            print(f"Failed to get sessions page: {response.status_code}")
            return

        csrf_token = get_csrf_token(response)

        # Attempt to revoke all sessions
        with self.client.post("/sessions/revoke-all", data={"csrf_token": csrf_token}, catch_response=True) as response:
            if response.status_code in [200, 302]:
                # 200 or redirect is expected
                response.success()
            else:
                response.failure(f"Revoke all failed: {response.status_code}")

        # After revoking, we should still be logged in with current session
        # Re-login for next iteration
        self.login()


if __name__ == "__main__":
    import os

    os.system(f"locust -f {__file__} --host={get_host_for_locust_testing()}")
