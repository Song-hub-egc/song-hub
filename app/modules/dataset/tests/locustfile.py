from locust import HttpUser, TaskSet, task, between
from core.environment.host import get_host_for_locust_testing

class UserBehavior(TaskSet):
    def on_start(self):
        # Simulate login if necessary or just browse public pages
        # For simplicity, we assume public access or we can implement login
        self.login()

    def login(self):
        response = self.client.get("/login")
        # In a real scenario, we would parse CSRF token and post to /login
        # For now, we assume anonymous browsing for some tasks
        pass

    @task(3)
    def index(self):
        self.client.get("/")

    @task(2)
    def list_datasets(self):
        self.client.get("/dataset/list")

    @task(1)
    def view_dataset(self):
        # View a specific dataset (assuming ID 1 exists and is public)
        self.client.get("/dataset/1")

    @task(1)
    def download_dataset(self):
        # Download a dataset
        self.client.get("/dataset/download/1")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
    host = get_host_for_locust_testing()
