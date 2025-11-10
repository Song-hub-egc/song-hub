import pytest
from datetime import datetime, timezone
from app import create_app, db
from app.modules.cart.models import Cart, CartItem
from app.modules.auth.models import User
from app.modules.dataset.models import DataSet, DSMetaData
from app.modules.featuremodel.models import FeatureModel

class TestCartModels:
    """Test cases for cart models."""

    @pytest.fixture(autouse=True)
    def setup(self, test_app, test_client):
        self.app = test_app
        self.client = test_client
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user
        self.user = User(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        db.session.add(self.user)
        
        # Create test dataset and feature model
        meta = DSMetaData(
            title='Test Dataset',
            description='Test Description',
            license='MIT',
            version='1.0'
        )
        db.session.add(meta)
        
        self.dataset = DataSet(
            user_id=self.user.id,
            meta_data=meta
        )
        db.session.add(self.dataset)
        
        self.feature_model = FeatureModel(
            name='Test Feature Model',
            data_set_id=self.dataset.id,
            user_id=self.user.id
        )
        db.session.add(self.feature_model)
        
        db.session.commit()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_cart_for_user(self):
        """Test creating a cart for a user."""
        cart = Cart(user_id=self.user.id)
        db.session.add(cart)
        db.session.commit()
        
        assert cart.id is not None
        assert cart.user_id == self.user.id
        assert cart.session_id is None
        assert isinstance(cart.created_at, datetime)
        assert isinstance(cart.updated_at, datetime)
        
    def test_create_cart_for_session(self):
        """Test creating a cart for a session."""
        session_id = 'test-session-123'
        cart = Cart(session_id=session_id)
        db.session.add(cart)
        db.session.commit()
        
        assert cart.id is not None
        assert cart.session_id == session_id
        assert cart.user_id is None
        
    def test_add_item_to_cart(self):
        """Test adding an item to the cart."""
        cart = Cart(user_id=self.user.id)
        db.session.add(cart)
        
        cart_item = CartItem(
            cart=cart,
            feature_model_id=self.feature_model.id
        )
        db.session.add(cart_item)
        db.session.commit()
        
        assert len(cart.items) == 1
        assert cart.items[0].id == cart_item.id
        assert cart.items[0].feature_model_id == self.feature_model.id
        
    def test_has_feature_model(self):
        """Test checking if a feature model is in the cart."""
        cart = Cart(user_id=self.user.id)
        cart_item = CartItem(
            cart=cart,
            feature_model_id=self.feature_model.id
        )
        db.session.add_all([cart, cart_item])
        db.session.commit()
        
        assert cart.has_feature_model(self.feature_model.id) is True
        assert cart.has_feature_model(999) is False  # Non-existent ID
        
    def test_cart_is_empty(self):
        """Test checking if cart is empty."""
        cart = Cart(user_id=self.user.id)
        db.session.add(cart)
        db.session.commit()
        
        assert cart.is_empty() is True
        
        cart_item = CartItem(
            cart=cart,
            feature_model_id=self.feature_model.id
        )
        db.session.add(cart_item)
        db.session.commit()
        
        assert cart.is_empty() is False
        
    def test_clear_cart(self):
        """Test clearing all items from the cart."""
        cart = Cart(user_id=self.user.id)
        cart_item = CartItem(
            cart=cart,
            feature_model_id=self.feature_model.id
        )
        db.session.add_all([cart, cart_item])
        db.session.commit()
        
        assert len(cart.items) == 1
        
        cart.clear()
        db.session.commit()
        
        assert len(cart.items) == 0
        assert CartItem.query.count() == 0
