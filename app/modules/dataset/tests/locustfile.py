from locust import HttpUser, TaskSet, between, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token


class DatasetBehavior(TaskSet):
    @task
    def dataset(self):
        response = self.client.get("/dataset/upload")
        get_csrf_token(response)
    @task
    def trending_home(self):
        self.client.get("/", name="trending_home")

class DatasetUser(HttpUser):
    wait_time = between(5, 9)
    host = get_host_for_locust_testing()
    tasks = [DatasetBehavior]

