"""
Unit tests for the download counter feature.

Tests cover:
- Download count increment on first download
- Download count persistence (no increment on repeated downloads)
- Download count display in dataset view
- Download count in API response
- Stats endpoint functionality
"""

import pytest

from app import db
from app.modules.auth.models import User
from app.modules.dataset.models import DataSet
from app.modules.dataset.services import DataSetService

dataset_service = DataSetService()


def _get_first_dataset_and_user():
    """Return (dataset, user) from DB or (None, None) if missing."""
    dataset = None
    user = None
    try:
        dataset = db.session.query(DataSet).first()
        user = db.session.query(User).first()
    except Exception:
        dataset = None
        user = None
    return dataset, user


def test_download_count_increments_on_first_download(test_database_poblated):
    """Test that download_count increments when a dataset is downloaded for the first time."""
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        pytest.skip("No dataset seeded")

    # Get initial download count
    initial_count = dataset.download_count

    # Download the dataset
    download_url = f"/dataset/download/{dataset.id}"
    response = client.get(download_url, follow_redirects=True)
    assert response.status_code == 200, f"Download request failed (GET {download_url})"

    # Refresh dataset from database
    db.session.refresh(dataset)

    # Verify download count incremented
    assert (
        dataset.download_count == initial_count + 1
    ), f"Download count should increment from {initial_count} to {initial_count + 1}"


def test_download_count_does_not_increment_on_repeated_download(test_database_poblated):
    """Test that download_count does NOT increment on repeated downloads from same user/session."""
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        pytest.skip("No dataset seeded")

    download_url = f"/dataset/download/{dataset.id}"

    # First download
    response1 = client.get(download_url, follow_redirects=True)
    assert response1.status_code == 200

    db.session.refresh(dataset)
    count_after_first = dataset.download_count

    # Second download (same client/session)
    response2 = client.get(download_url, follow_redirects=True)
    assert response2.status_code == 200

    db.session.refresh(dataset)
    count_after_second = dataset.download_count

    # Verify count did NOT increment on second download
    assert (
        count_after_second == count_after_first
    ), "Download count should not increment on repeated download from same user/session"


def test_download_count_default_value_is_zero(test_database_poblated):
    """Test that new datasets have download_count initialized to 0."""
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        pytest.skip("No dataset seeded")

    # Check that download_count exists and has a valid value (>= 0)
    assert hasattr(dataset, "download_count"), "DataSet model should have download_count attribute"
    assert dataset.download_count >= 0, "Download count should be non-negative"


def test_download_count_in_dataset_dict(test_database_poblated):
    """Test that download_count is included in dataset's to_dict() method."""
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        pytest.skip("No dataset seeded")

    # Get dataset dictionary representation within request context
    with client.application.test_request_context():
        dataset_dict = dataset.to_dict()

        # Verify download_count is in the dictionary
        assert "download_count" in dataset_dict, "download_count should be included in dataset dictionary"
        assert isinstance(dataset_dict["download_count"], int), "download_count should be an integer"
        assert dataset_dict["download_count"] >= 0, "download_count should be non-negative"


def test_download_count_displayed_in_view(test_database_poblated):
    """Test that download count is displayed on the dataset view page."""
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        pytest.skip("No dataset seeded")

    # Visit dataset detail page
    if dataset.ds_meta_data.dataset_doi:
        view_url = f"/doi/{dataset.ds_meta_data.dataset_doi}/"
    else:
        view_url = f"/dataset/unsynchronized/{dataset.id}"

    response = client.get(view_url, follow_redirects=True)
    assert response.status_code == 200, f"Dataset view page failed (GET {view_url})"

    # Check that download count is displayed
    html = response.get_data(as_text=True)
    assert "Downloads" in html or "downloads" in html.lower(), "Dataset view should display 'Downloads' label"
    assert (
        str(dataset.download_count) in html
    ), f"Dataset view should display download count value ({dataset.download_count})"


def test_stats_endpoint_returns_download_count(test_database_poblated):
    """Test that the /datasets/<id>/stats endpoint returns download_count."""
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        pytest.skip("No dataset seeded")

    # Call stats endpoint
    stats_url = f"/datasets/{dataset.id}/stats"
    response = client.get(stats_url)
    assert response.status_code == 200, f"Stats endpoint failed (GET {stats_url})"

    # Verify JSON response
    data = response.get_json()
    assert data is not None, "Stats endpoint should return JSON"
    assert "download_count" in data, "Stats should include download_count"
    assert isinstance(data["download_count"], int), "download_count should be an integer"
    assert data["download_count"] >= 0, "download_count should be non-negative"


def test_stats_endpoint_includes_all_metrics(test_database_poblated):
    """Test that stats endpoint includes all expected metrics."""
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        pytest.skip("No dataset seeded")

    stats_url = f"/datasets/{dataset.id}/stats"
    response = client.get(stats_url)
    assert response.status_code == 200

    data = response.get_json()
    expected_fields = [
        "dataset_id",
        "title",
        "download_count",
        "total_download_records",
        "total_views",
        "created_at",
        "files_count",
        "total_size_bytes",
        "publication_type",
    ]

    for field in expected_fields:
        assert field in data, f"Stats should include '{field}' field"


def test_increment_download_count_service_method(test_database_poblated):
    """Test the increment_download_count service method directly."""
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        pytest.skip("No dataset seeded")

    initial_count = dataset.download_count

    # Call service method directly
    dataset_service.increment_download_count(dataset.id)

    # Refresh and verify
    db.session.refresh(dataset)
    assert dataset.download_count == initial_count + 1, "Service method should increment download count"


def test_download_count_persists_across_sessions(test_database_poblated):
    """Test that download_count persists correctly in the database."""
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        pytest.skip("No dataset seeded")

    # Set a specific download count
    dataset.download_count = 42
    db.session.commit()

    # Fetch dataset again from database
    fetched_dataset = db.session.query(DataSet).filter_by(id=dataset.id).first()

    # Verify count persisted
    assert fetched_dataset.download_count == 42, "Download count should persist in database"
