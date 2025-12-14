from locust import HttpUser, TaskSet, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import fake, get_csrf_token


class SignupBehavior(TaskSet):
    def on_start(self):
        self.signup()

    @task
    def signup(self):
        response = self.client.get("/signup")
        csrf_token = get_csrf_token(response)

        response = self.client.post(
            "/signup", data={"email": fake.email(), "password": fake.password(), "csrf_token": csrf_token}
        )
        if response.status_code != 200:
            print(f"Signup failed: {response.status_code}")


class LoginBehavior(TaskSet):
    def on_start(self):
        self.ensure_logged_out()
        self.login()

    @task
    def ensure_logged_out(self):
        response = self.client.get("/logout")
        if response.status_code != 200:
            print(f"Logout failed or no active session: {response.status_code}")

    @task
    def login(self):
        response = self.client.get("/login")
        if response.status_code != 200 or "Login" not in response.text:
            print("Already logged in or unexpected response, redirecting to logout")
            self.ensure_logged_out()
            response = self.client.get("/login")

        csrf_token = get_csrf_token(response)

        response = self.client.post(
            "/login", data={"email": "user1@example.com", "password": "1234", "csrf_token": csrf_token}
        )
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")


class TwoFactorBehavior(TaskSet):
    def on_start(self):
        self.login()

    def login(self):
        response = self.client.get("/login")
        csrf_token = get_csrf_token(response)

        self.client.post(
            "/login",
            data={"email": "user1@example.com", "password": "1234", "csrf_token": csrf_token},
        )

    @task
    def setup_2fa(self):
        """
        Simulate the flow of setting up 2FA.
        """
        # 1. Access the setup page
        response = self.client.get("/profile/two-factor/setup", name="2FA Setup Page")
        csrf_token = get_csrf_token(response)

        if response.status_code == 200:
            # 2. Simulate enabling 2FA (this would normally require scanning QR and entering code)
            # For load testing, we mostly care about the endpoint responding.
            # We can try to hit the verify endpoint with an invalid token to check load on verification logic.
            self.client.post(
                "/profile/two-factor/verify",
                json={"token": "000000"}, # Invalid token, but stresses the server
                headers={"X-CSRFToken": csrf_token},
                name="2FA Verify (Simulated)"
            )


class AuthUser(HttpUser):
    tasks = [SignupBehavior, LoginBehavior, TwoFactorBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()

