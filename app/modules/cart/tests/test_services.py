import pytest
from unittest.mock import patch, MagicMock
from flask import session
from app import create_app, db
from app.modules.cart.models import Cart, CartItem
from app.modules.cart.services import CartService
from app.modules.auth.models import User
from app.modules.dataset.models import DataSet, DSMetaData
from app.modules.featuremodel.models import FeatureModel

class TestCartService:
    """Test cases for CartService."""

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
        
        # Create a second feature model
        self.feature_model2 = FeatureModel(
            name='Test Feature Model 2',
            data_set_id=self.dataset.id,
            user_id=self.user.id
        )
        db.session.add(self.feature_model2)
        
        db.session.commit()
        
        self.service = CartService()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_or_create_cart_for_user(self, test_client):
        """Test getting or creating a cart for an authenticated user."""
        with test_client:
            # Simulate authenticated user
            with patch('flask_login.utils._get_user', return_value=self.user):
                cart = self.service.get_or_create_cart()
                
                assert cart is not None
                assert cart.user_id == self.user.id
                assert cart.session_id is None
                
                # Test getting the same cart again
                same_cart = self.service.get_or_create_cart()
                assert cart.id == same_cart.id
    
    def test_get_or_create_cart_for_session(self, test_client):
        """Test getting or creating a cart for an anonymous user."""
        with test_client:
            # Simulate anonymous user
            with patch('flask_login.utils._get_user', return_value=MagicMock(is_authenticated=False)):
                cart = self.service.get_or_create_cart()
                
                assert cart is not None
                assert cart.user_id is None
                assert cart.session_id is not None
                assert 'cart_session_id' in session
                
                # Test getting the same cart again
                same_cart = self.service.get_or_create_cart()
                assert cart.id == same_cart.id
    
    def test_add_to_cart(self, test_client):
        """Test adding an item to the cart."""
        with test_client:
            with patch('flask_login.utils._get_user', return_value=self.user):
                # Add first item
                result = self.service.add_to_cart(self.feature_model.id)
                assert result['success'] is True
                assert result['message'] == 'Added to cart'
                assert result['cart_count'] == 1
                
                # Try adding the same item again
                result = self.service.add_to_cart(self.feature_model.id)
                assert result['success'] is False
                assert 'already in cart' in result['message']
                
                # Add a different item
                result = self.service.add_to_cart(self.feature_model2.id)
                assert result['success'] is True
                assert result['cart_count'] == 2
    
    def test_remove_from_cart(self, test_client):
        """Test removing an item from the cart."""
        with test_client:
            with patch('flask_login.utils._get_user', return_value=self.user):
                # Add items to cart
                self.service.add_to_cart(self.feature_model.id)
                result = self.service.add_to_cart(self.feature_model2.id)
                cart_item_id = CartItem.query.filter_by(
                    feature_model_id=self.feature_model2.id
                ).first().id
                
                # Remove item
                result = self.service.remove_from_cart(cart_item_id)
                assert result['success'] is True
                assert result['message'] == 'Removed from cart'
                assert result['cart_count'] == 1
                
                # Try removing non-existent item
                result = self.service.remove_from_cart(999)
                assert result['success'] is False
    
    def test_clear_cart(self, test_client):
        """Test clearing all items from the cart."""
        with test_client:
            with patch('flask_login.utils._get_user', return_value=self.user):
                # Add items to cart
                self.service.add_to_cart(self.feature_model.id)
                self.service.add_to_cart(self.feature_model2.id)
                
                # Clear cart
                result = self.service.clear_cart()
                assert result['success'] is True
                assert result['message'] == 'Cart cleared'
                assert result['cart_count'] == 0
    
    def test_get_cart_items(self, test_client):
        """Test getting all items in the cart."""
        with test_client:
            with patch('flask_login.utils._get_user', return_value=self.user):
                # Add items to cart
                self.service.add_to_cart(self.feature_model.id)
                self.service.add_to_cart(self.feature_model2.id)
                
                # Get cart items
                items = self.service.get_cart_items()
                assert len(items) == 2
                assert items[0]['feature_model_id'] == self.feature_model.id
                assert items[1]['feature_model_id'] == self.feature_model2.id
    
    def test_merge_session_cart_on_login(self, test_client):
        """Test merging session cart with user cart on login."""
        with test_client:
            # First, create a session cart as anonymous user
            with patch('flask_login.utils._get_user', return_value=MagicMock(is_authenticated=False)):
                session_cart = self.service.get_or_create_cart()
                self.service.add_to_cart(self.feature_model.id)
                
                # Now simulate login
                with patch('flask_login.utils._get_user', return_value=self.user):
                    # Create a user cart with a different item
                    user_cart = self.service.get_or_create_cart()
                    self.service.add_to_cart(self.feature_model2.id)
                    
                    # Merge carts
                    self.service.merge_session_cart_on_login(self.user.id)
                    
                    # Check that user cart now has both items
                    items = self.service.get_cart_items()
                    assert len(items) == 2
                    assert any(item['feature_model_id'] == self.feature_model.id for item in items)
                    assert any(item['feature_model_id'] == self.feature_model2.id for item in items)
                    
                    # Check that session cart was deleted
                    assert session.get('cart_session_id') is None
