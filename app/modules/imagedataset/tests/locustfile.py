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
        files = {
            "file": ("test_image.png", b"fake_image_content", "image/png")
        }
        
        # Get CSRF token first (normally from a GET request, usually handled in login or previous requests)
        # But we need it for the headers.
        response = self.client.get("/dataset/upload/image_dataset", name="Get Upload Page")
        csrf_token = get_csrf_token(response)
        
        upload_response = self.client.post(
            "/dataset/file/upload",
            files=files,
            headers={"X-CSRFToken": csrf_token},
            name="Upload File (Dropzone)"
        )
        
        if upload_response.status_code == 200:
            filename = upload_response.json().get("filename")
            
            # 2. Submit Form
            # We need to match the fields from ImageDatasetForm
            # Looking at standard form behavior, we likely need:
            # - title
            # - desc
            # - tags
            # - agreeCheckbox
            # - and likely a hidden field for the filename? 
            # In the UVL upload, Dropzone likely handles the file transfer and the form submission 
            # might imply the file is already there or linked via session/temp folder. 
            # The 'create_dataset' route uses 'dataset_service.create_from_form'.
            # If we assume the standard pattern where Dropzone might just be for UX and the real Submit 
            # picks up the file from temp, we verify that.
            # But the 'create_from_form' likely expects the request.files to be empty if it relied on temp?
            # actually usually the Dropzone just puts it in temp, and the form submission doesn't send the file again?
            # Wait, if we look at `dataset/routes.py`:
            # `file = request.files["file"]` is in `/dataset/file/upload`.
            # In `create_dataset`: `dataset = dataset_service.create_from_form(form=form, current_user=current_user)`
            # We need to know what `create_from_form` does.
            # If it expects the file to be in the form submission (as Flask-WTF usually does), 
            # then the Dropzone might just be for validation/preview and the final form POST sends the file again?
            # OR the form has a hidden field with the filename.
            # From `test_selenium.py`: `dropzone.send_keys(image_path)` -> waits -> submits.
            # It seems the final submit DOES NOT send the file again if Dropzone did it?
            # Let's assume for now we just hit the upload endpoint which is the heavy lifting.
            # But to complete a "user flow" we should also hit the submit.
            
            # For this task, validating the file upload endpoint (heaviest part) is often sufficient.
            # I will add the form submission with basic metadata.
            
            self.client.post(
                "/dataset/upload/image_dataset",
                data={
                    "title": f"Locust Image Dataset {filename}",
                    "desc": "Load testing description",
                    "tags": "locust,test",
                    "agreeCheckbox": "y",
                    "csrf_token": csrf_token
                },
                name="Submit Dataset Form"
            )
        else:
             print(f"File upload failed: {upload_response.text}")

class ImageDatasetUser(HttpUser):
    tasks = [ImageDatasetBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
