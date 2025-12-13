import json

from app.modules.auth.models import User
from app.modules.cart.repositories import CartRepository
from app.modules.dataset.models import DataSet, DSMetaData, PublicationType
from app.modules.featuremodel.models import FeatureModel, FMMetaData


# Test covering the Model creation and Repository logic
def test_cart_repository_operations(test_client):
    """
    Test the CartRepository basic operations: create, get, add item.
    """
    repo = CartRepository()

    # Simulate a user (User model only accepts columns in kwargs)
    user = User(email="cart_repo_test@example.com", password="password")
    from app import db

    db.session.add(user)
    db.session.commit()

    # Test Create
    cart = repo.get_or_create_for_user(user.id)
    assert cart is not None
    assert cart.user_id == user.id

    # Create required data for FeatureModel
    # 1. DSMetaData
    ds_meta = DSMetaData(
        title="Test DS", description="Desc", publication_type=PublicationType.OTHER, deposition_id=12345
    )
    db.session.add(ds_meta)
    db.session.commit()

    # 2. DataSet
    ds = DataSet(user_id=user.id, ds_meta_data_id=ds_meta.id)
    db.session.add(ds)
    db.session.commit()

    # 3. FMMetaData
    fm_meta = FMMetaData(
        uvl_filename="fm1.uvl", title="FM1", description="Desc", publication_type=PublicationType.OTHER
    )
    db.session.add(fm_meta)
    db.session.commit()

    # 4. FeatureModel
    fm = FeatureModel(data_set_id=ds.id, fm_meta_data_id=fm_meta.id)
    db.session.add(fm)
    db.session.commit()

    # Test Add Item
    item = repo.add_item(cart, fm.id)
    assert item.feature_model_id == fm.id
    assert repo.get_item_count(cart) == 1

    # Test Clear
    repo.clear_cart(cart)
    assert repo.get_item_count(cart) == 0


# Test covering Service logic and API Endpoints
def test_cart_service_and_api(test_client):
    """
    Test the CartService and API endpoints.
    """
    from app import db

    # Setup User & FeatureModel (Reuse simpler setup if possible, or repeat)
    user = User(email="cart_service_test@example.com", password="password")
    db.session.add(user)
    db.session.commit()

    ds_meta = DSMetaData(
        title="Test DS Service", description="Desc", publication_type=PublicationType.OTHER, deposition_id=54321
    )
    db.session.add(ds_meta)
    db.session.commit()

    ds = DataSet(user_id=user.id, ds_meta_data_id=ds_meta.id)
    db.session.add(ds)
    db.session.commit()

    fm_meta = FMMetaData(
        uvl_filename="service.uvl", title="Service FM", description="Desc", publication_type=PublicationType.OTHER
    )
    db.session.add(fm_meta)
    db.session.commit()

    fm = FeatureModel(data_set_id=ds.id, fm_meta_data_id=fm_meta.id)
    db.session.add(fm)
    db.session.commit()

    # 1. Test Adding via API (POST /cart/add/<id>)
    # This implicitly tests the Service's add_to_cart method
    response = test_client.post(f"/cart/add/{fm.id}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True

    # 2. Test Getting Cart Count via API
    response = test_client.get("/cart/count")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["count"] == 1


# Test covering the existence of the Cart Page
def test_cart_ui_route(test_client):
    """
    Test that the Cart UI route is accessible and renders the template.
    """
    response = test_client.get("/cart")
    assert response.status_code == 200
    assert b"My Cart" in response.data
