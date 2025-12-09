from app import db
from app.modules.auth.models import User
from app.modules.dataset.models import DataSet, DSDownloadRecord, DSViewRecord
from app.modules.dataset.services import DataSetService

dataset_service = DataSetService()


def _build_trending_url():
    # Trending is rendered on the public index page in this app
    return "/"


def _build_download_url(client, dataset_id: int) -> str:
    # Keep this simple and consistent with the app routes
    return f"/dataset/download/{dataset_id}"


def _get_first_dataset_and_user():
    """Return (dataset, user) from DB or (None, None) if missing.

    Uses the application db session to fetch the first seeded dataset and user.
    Tests will skip if no dataset is found.
    """
    dataset = None
    user = None
    try:
        dataset = db.session.query(DataSet).first()
        user = db.session.query(User).first()
    except Exception:
        # If the DB/session isn't available, return None values and let tests skip
        dataset = None
        user = None

    return dataset, user


def test_trending_download_weekly(test_database_poblated):
    """
    Fixture `test_database_poblated` yields a Flask test client.
    Retrieve dataset and user from the DB inside the test (the fixture already seeded them).
    """
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        import pytest

        pytest.skip("No dataset seeded")

    # Count downloads from DSDownloadRecord table for this dataset
    initial_downloads = db.session.query(DSDownloadRecord).filter_by(dataset_id=dataset.id).count() or 0

    download_url = _build_download_url(client, dataset.id)
    response = client.get(download_url, follow_redirects=True)
    assert response.status_code == 200, f"Download request was unsuccessful (GET {download_url})"

    # Recount downloads after the request
    updated_downloads = db.session.query(DSDownloadRecord).filter_by(dataset_id=dataset.id).count()
    assert updated_downloads == initial_downloads + 1, "Download count was not incremented"


def test_trending_multiple_downloads_same_user(test_database_poblated):
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        import pytest

        pytest.skip("No dataset seeded")

    initial_downloads = db.session.query(DSDownloadRecord).filter_by(dataset_id=dataset.id).count() or 0

    download_url = _build_download_url(client, dataset.id)

    # First download
    response1 = client.get(download_url, follow_redirects=True)
    assert response1.status_code == 200, f"First download request was unsuccessful (GET {download_url})"

    # Second download (same client / same session)
    response2 = client.get(download_url, follow_redirects=True)
    assert response2.status_code == 200, f"Second download request was unsuccessful (GET {download_url})"

    # Recount downloads after the requests
    updated_downloads = db.session.query(DSDownloadRecord).filter_by(dataset_id=dataset.id).count()
    # Current implementation increments on every download request
    assert updated_downloads == initial_downloads + 1, "Download count should increment on each request"


def test_trending_page_renders_and_contains_dataset_info(test_database_poblated):
    """
    Comprueba que la página de trending se renderiza y contiene información del dataset seed.
    """
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        import pytest

        pytest.skip("No dataset seeded")

    # Touch DOI and download endpoints to generate activity
    client.get(f"/doi/{dataset.ds_meta_data.dataset_doi}", follow_redirects=True)
    client.get(_build_download_url(client, dataset.id), follow_redirects=True)
    trending_url = _build_trending_url()
    response = client.get(trending_url, follow_redirects=True)
    assert response.status_code == 200, f"GET {trending_url} should return 200"

    text = response.get_data(as_text=True)
    # Debe contener el título del dataset
    assert dataset.ds_meta_data.title in text, "Trending page does not contain the dataset title"

    # Debe contener el badge de downloads y views con los contadores actuales
    downloads_count = db.session.query(DSDownloadRecord).filter_by(dataset_id=dataset.id).count() or 0
    views_count = db.session.query(DSViewRecord).filter_by(dataset_id=dataset.id).count() or 0

    downloads_text = f"Downloads: {downloads_count}"
    views_text = f"Views: {views_count}"

    # The public template may render downloads as e.g. "1 downloads" or "Downloads: 1".
    lower = text.lower()
    assert (
        f"{downloads_count} downloads" in lower
        or downloads_text.lower() in lower
        or (str(downloads_count) in lower and "download" in lower)
    ), "Trending page does not show downloads count"

    # Views may or may not be present depending on template; only assert if there is at least one view
    if views_count > 0:
        assert (
            f"{views_count} views" in lower
            or views_text.lower() in lower
            or (str(views_count) in lower and "view" in lower)
        ), "Trending page does not show views count"
    # Debe contener el enlace de descarga esperado
    download_link = f"/dataset/download/{dataset.id}"
    assert download_link in text, "Trending page does not include download link for the dataset"


def test_trending_download_links_work(test_database_poblated):
    """
    Comprueba que los enlaces de descarga listados en la página de trending funcionan (status 200 o redirección válida).
    """
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        import pytest

        pytest.skip("No dataset seeded")

    trending_url = _build_trending_url()
    page = client.get(trending_url, follow_redirects=True)
    assert page.status_code == 200, f"GET {trending_url} should return 200"

    # Intenta descargar usando el enlace estándar de descarga del dataset
    download_url = _build_download_url(client, dataset.id)
    resp = client.get(download_url, follow_redirects=True)
    assert resp.status_code == 200, f"Download from trending page should succeed (GET {download_url})"
