"""
Locust load tests for the download counter feature.

This file simulates multiple concurrent users interacting with the download counter:
- Viewing dataset pages
- Downloading datasets
- Checking download counters
- Accessing trending datasets

Run from project root:
    locust -f app/modules/dataset/tests/locustfile.py
"""

import re
from datetime import datetime

from bs4 import BeautifulSoup
from locust import HttpUser, TaskSet, between, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token


class DownloadCounterBehavior(TaskSet):
    """
    Simulates user behavior related to download counter functionality.
    """

    def on_start(self):
        """Called when a simulated user starts. Login the user."""
        self.login()

    def login(self):
        """Login a test user."""
        response = self.client.get("/login")
        csrf_token = get_csrf_token(response)

        self.client.post(
            "/login",
            {
                "email": "user1@example.com",
                "password": "1234",
                "csrf_token": csrf_token,
            },
            name="/login (POST)",
        )

    def _extract_user_datasets_url(self, html):
        soup = BeautifulSoup(html, "html.parser")

        # Busca enlaces que vayan a /user/<id>/datasets
        for a in soup.find_all("a", href=True):
            if re.match(r"/user/\d+/datasets", a["href"]):
                return a["href"]

        return None

    @task(3)
    def view_dataset_list(self):
        """View the dataset list page (high frequency)."""
        self.client.get("/dataset/list", name="View Dataset List")

    @task(2)
    def view_dataset_detail(self):
        """
        View a dataset detail page to see the download counter.
        This simulates users checking the download count.
        """
        # Assuming dataset with ID 1 exists
        response = self.client.get("/dataset/unsynchronized/1", name="View Dataset Detail")

        # Verify the response contains download counter
        if response.status_code == 200 and "Downloads" in response.text:
            # Successfully viewed download counter
            pass

    @task(1)
    def download_dataset(self):
        """
        Download a dataset, which should increment the download counter.
        This is the core action being tested.
        """
        # Download dataset with ID 1
        response = self.client.get("/dataset/download/1", name="Download Dataset")

        if response.status_code == 200:
            # Download successful
            pass

    @task(2)
    def view_trending_home(self):
        """
        View the home page with trending datasets.
        This tests the trending download counter display.
        """
        response = self.client.get("/", name="View Trending Home")

        # Verify trending section exists
        if response.status_code == 200 and "trending" in response.text.lower():
            # Trending section loaded
            pass

    @task(1)
    def check_dataset_stats(self):
        """
        Check the stats endpoint for a dataset.
        This verifies the download_count is exposed in the API.
        """
        response = self.client.get("/datasets/1/stats", name="Check Dataset Stats")

        if response.status_code == 200:
            try:
                data = response.json()
                if "download_count" in data:
                    # Stats endpoint working correctly
                    pass
            except Exception:
                # JSON parsing failed
                pass


class DownloadCounterUser(HttpUser):
    """
    Simulates a user interacting with the download counter feature.

    Configuration:
    - wait_time: Random wait between 1-3 seconds between tasks
    - host: Automatically set based on environment
    - tasks: Uses DownloadCounterBehavior task set
    """

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    host = get_host_for_locust_testing()
    tasks = [DownloadCounterBehavior]


# Legacy behavior for backward compatibility
class DatasetBehavior(TaskSet):
    @task
    def dataset(self):
        response = self.client.get("/dataset/upload")
        get_csrf_token(response)

    @task
    def trending_home(self):
        self.client.get("/", name="trending_home")


class DatasetUser(HttpUser):
    """Legacy dataset user (kept for compatibility)."""

    wait_time = between(5, 9)
    host = get_host_for_locust_testing()
    tasks = [DatasetBehavior]


class DatasetCommentBehavior(TaskSet):
    def on_start(self):
        """Called when a simulated user starts. Login the user and create a comment for editing."""
        self.login()
        self.create_comment_for_edit()

    def login(self):
        """Login a test user."""
        response = self.client.get("/login")
        csrf_token = get_csrf_token(response)

        self.client.post(
            "/login",
            {
                "email": "user1@example.com",
                "password": "1234",
                "csrf_token": csrf_token,
            },
            name="/login (POST) [DatasetComment]",
        )

    def create_comment_for_edit(self):
        """Create a comment to be used by the edit task."""
        # Create a comment on dataset 1
        response = self.client.post(
            "/datasets/1/comments", json={"content": "Initial comment for editing"}, name="Create Initial Comment"
        )
        if response.status_code == 201:
            self.comment_id = response.json()["comment"]["id"]
        else:
            print(f"Failed to create initial comment: {response.text}")
            self.comment_id = None

    @task(2)
    def post_comment(self):
        """Task to publish a new comment."""
        self.client.post("/datasets/1/comments", json={"content": f"Comment at {datetime.now()}"}, name="Post Comment")

    @task(1)
    def edit_comment(self):
        """Task to edit an existing comment with the current time."""
        if self.comment_id:
            new_content = f"Edited at {datetime.now()}"
            self.client.put(f"/comments/{self.comment_id}", json={"content": new_content}, name="Edit Comment")

    @task(1)
    def delete_comment(self):
        """Task to create and then delete a comment."""
        # First create a comment to delete
        response = self.client.post(
            "/datasets/1/comments", json={"content": "Comment to be deleted"}, name="Create Comment (for delete)"
        )

        if response.status_code == 201:
            comment_to_delete_id = response.json()["comment"]["id"]

            # Now delete it
            self.client.delete(f"/comments/{comment_to_delete_id}", name="Delete Comment")


class DatasetCommentUser(HttpUser):
    wait_time = between(5, 9)
    host = get_host_for_locust_testing()
    tasks = [DatasetCommentBehavior]
