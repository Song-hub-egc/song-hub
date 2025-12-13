from io import BytesIO

import pytest
from flask import Flask

from app.modules.fakenodo.routes import fakenodo_bp
from app.modules.fakenodo.services import fakenodo_service


@pytest.fixture(autouse=True)
def reset_fakenodo_service():
    fakenodo_service.reset()
    yield
    fakenodo_service.reset()


@pytest.fixture()
def fakenodo_client():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(fakenodo_bp)
    with app.test_client() as client:
        yield client


def _create_deposition(client, metadata=None):
    payload = {"metadata": metadata} if metadata is not None else {"metadata": {}}
    resp = client.post("/fakenodo/api/", json=payload)
    assert resp.status_code == 201
    return resp.get_json()


def test_create_deposition_has_expected_fields(fakenodo_client):
    metadata = {"title": "Demo dataset"}
    created = _create_deposition(fakenodo_client, metadata)

    assert created["metadata"] == metadata
    assert "id" in created
    assert created.get("conceptrecid") == 101


def test_get_deposition_returns_metadata_and_version(fakenodo_client):
    metadata = {"title": "Demo dataset"}
    created = _create_deposition(fakenodo_client, metadata)
    deposition_id = created["id"]

    get_resp = fakenodo_client.get(f"/fakenodo/api/{deposition_id}")
    assert get_resp.status_code == 200
    fetched = get_resp.get_json()
    assert fetched["metadata"] == metadata
    assert fetched["version"] == 1


def test_update_deposition_metadata(fakenodo_client):
    created = _create_deposition(fakenodo_client, {"title": "Demo"})
    deposition_id = created["id"]

    updated_metadata = {"title": "Updated title"}
    update_resp = fakenodo_client.patch(f"/fakenodo/api/{deposition_id}", json={"metadata": updated_metadata})
    assert update_resp.status_code == 200
    assert update_resp.get_json()["metadata"] == updated_metadata


def test_upload_file_creates_file_entry(fakenodo_client):
    created = _create_deposition(fakenodo_client, {"title": "Demo"})
    deposition_id = created["id"]

    upload_resp = fakenodo_client.post(
        f"/fakenodo/api/{deposition_id}/files",
        data={"file": (BytesIO(b"hello world"), "file1.txt")},
        content_type="multipart/form-data",
    )
    assert upload_resp.status_code == 201
    assert upload_resp.get_json()["filename"] == "file1.txt"


def test_publish_creates_initial_version(fakenodo_client):
    created = _create_deposition(fakenodo_client, {"title": "Demo"})
    deposition_id = created["id"]

    # upload and publish
    fakenodo_client.post(
        f"/fakenodo/api/{deposition_id}/files",
        data={"file": (BytesIO(b"hello world"), "file1.txt")},
        content_type="multipart/form-data",
    )
    publish_resp = fakenodo_client.post(f"/fakenodo/api/{deposition_id}/actions/publish")
    assert publish_resp.status_code == 202
    assert publish_resp.get_json()["version"] == 1


def test_publish_no_change_returns_same_version(fakenodo_client):
    created = _create_deposition(fakenodo_client, {"title": "Demo"})
    deposition_id = created["id"]

    fakenodo_client.post(
        f"/fakenodo/api/{deposition_id}/files",
        data={"file": (BytesIO(b"hello world"), "file1.txt")},
        content_type="multipart/form-data",
    )
    # first publish
    fakenodo_client.post(f"/fakenodo/api/{deposition_id}/actions/publish")
    # publish again without changes
    publish_again = fakenodo_client.post(f"/fakenodo/api/{deposition_id}/actions/publish")
    assert publish_again.status_code == 200
    assert publish_again.get_json()["version"] == 1


def test_publish_new_version_after_adding_file(fakenodo_client):
    created = _create_deposition(fakenodo_client, {"title": "Demo"})
    deposition_id = created["id"]

    fakenodo_client.post(
        f"/fakenodo/api/{deposition_id}/files",
        data={"file": (BytesIO(b"hello world"), "file1.txt")},
        content_type="multipart/form-data",
    )
    fakenodo_client.post(f"/fakenodo/api/{deposition_id}/actions/publish")

    # add second file
    upload_second = fakenodo_client.post(
        f"/fakenodo/api/{deposition_id}/files",
        data={"file": (BytesIO(b"more data"), "file2.txt")},
        content_type="multipart/form-data",
    )
    assert upload_second.status_code == 201

    publish_second_version = fakenodo_client.post(f"/fakenodo/api/deposit/depositions/{deposition_id}/actions/publish")
    assert publish_second_version.status_code == 202
    assert publish_second_version.get_json()["version"] == 2


def test_versions_list_and_delete(fakenodo_client):
    created = _create_deposition(fakenodo_client, {"title": "Demo"})
    deposition_id = created["id"]

    # create two versions
    fakenodo_client.post(
        f"/fakenodo/api/{deposition_id}/files",
        data={"file": (BytesIO(b"hello world"), "file1.txt")},
        content_type="multipart/form-data",
    )
    fakenodo_client.post(f"/fakenodo/api/{deposition_id}/actions/publish")
    fakenodo_client.post(
        f"/fakenodo/api/{deposition_id}/files",
        data={"file": (BytesIO(b"more data"), "file2.txt")},
        content_type="multipart/form-data",
    )
    fakenodo_client.post(f"/fakenodo/api/{deposition_id}/actions/publish")

    versions_resp = fakenodo_client.get(f"/fakenodo/api/{deposition_id}/versions")
    versions = versions_resp.get_json()
    assert versions_resp.status_code == 200
    assert len(versions) == 2
    assert versions[-1]["version"] == 2

    delete_resp = fakenodo_client.delete(f"/fakenodo/api/{deposition_id}")
    assert delete_resp.status_code == 204

    get_after_delete = fakenodo_client.get(f"/fakenodo/api/{deposition_id}")
    assert get_after_delete.status_code == 404
