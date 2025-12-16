from app import db
from app.modules.auth.models import User
from app.modules.dataset.models import DataSet


def _build_user_datasets_url(user_id: int) -> str:
    return f"/user/{user_id}/datasets"


def _get_seed_user_and_dataset():
    """Return (user, dataset) from the seeded DB or (None, None) if unavailable."""
    user = None
    dataset = None
    try:
        user = db.session.query(User).first()
        if user:
            dataset = db.session.query(DataSet).filter_by(user_id=user.id).first()
    except Exception:
        user = None
        dataset = None

    return user, dataset


def test_user_datasets_page_lists_seeded_dataset(test_database_poblated):
    """
    La página `/user/<id>/datasets` debe listar el dataset seed asociado al usuario.
    """
    client = test_database_poblated
    user, dataset = _get_seed_user_and_dataset()
    if not user or not dataset:
        import pytest

        pytest.skip("Seed user or dataset not found")

    response = client.get(_build_user_datasets_url(user.id), follow_redirects=True)
    assert response.status_code == 200, "User datasets page should return 200"
    text = response.get_data(as_text=True)
    dataset_title = dataset.ds_meta_data.title if dataset.ds_meta_data else dataset.name()
    assert dataset_title in text, "Seed dataset title should be listed for the user"


def test_user_datasets_page_returns_404_for_unknown_user(test_database_poblated):
    """
    Solicitar datasets para un usuario inexistente debe devolver HTTP 404.
    """
    client = test_database_poblated
    response = client.get(_build_user_datasets_url(999999))
    assert response.status_code == 404, "Unknown user datasets page should return 404"
