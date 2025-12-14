from locust import HttpUser, TaskSet, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token


class ImageDatasetBehavior(TaskSet):
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
    def view_image_upload_page(self):
        """
        View the upload page for image datasets.
        """
        self.client.get("/dataset/upload/image_dataset", name="View Image Upload Page")

    @task
    def upload_image_dataset(self):
        """
        Simulate uploading an image dataset.
        1. Upload the file to the temp folder via Dropzone endpoint.
        2. Submit the form with the filename returned from step 1.
        """
        # 1. Upload File
        # We need a file to upload. We can use a small dummy file or read checking if it exists
        # For performance testing, we can generate a small in-memory file.
        files = {"file": ("test_image.png", b"fake_image_content", "image/png")}

        # Get CSRF token first (normally from a GET request, usually handled in login or previous requests)
        # But we need it for the headers.
        response = self.client.get("/dataset/upload/image_dataset", name="Get Upload Page")
        csrf_token = get_csrf_token(response)

        upload_response = self.client.post(
            "/dataset/file/upload", files=files, headers={"X-CSRFToken": csrf_token}, name="Upload File (Dropzone)"
        )

        if upload_response.status_code == 200:
            filename = upload_response.json().get("filename")

            # 2. Submit Form
            self.client.post(
                "/dataset/upload/image_dataset",
                data={
                    "title": f"Locust Image Dataset {filename}",
                    "desc": "Load testing description",
                    "tags": "locust,test",
                    "agreeCheckbox": "y",
                    "csrf_token": csrf_token,
                },
                name="Submit Dataset Form",
            )
        else:
            print(f"File upload failed: {upload_response.text}")


class ImageDatasetUser(HttpUser):
    tasks = [ImageDatasetBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
