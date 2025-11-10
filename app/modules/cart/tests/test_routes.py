import pytest
from unittest.mock import patch, MagicMock
from flask import session, url_for
from app import create_app, db
from app.modules.cart.models import Cart, CartItem
from app.modules.user.models import User
from app.modules.dataset.models import DataSet, DSMetaData
from app.modules.featuremodel.models import FeatureModel

class TestCartRoutes:
    """Test cases for cart routes."""

    @pytest.fixture(autouse=True)
    def setup(self, app, client):
        self.app = app
        self.client = client
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
        
        # Create a cart for the user
        self.cart = Cart(user_id=self.user.id)
        db.session.add(self.cart)
        
        # Add an item to the cart
        self.cart_item = CartItem(
            cart=self.cart,
            feature_model_id=self.feature_model.id
        )
        db.session.add(self.cart_item)
        db.session.commit()
        
        self.client = self.app.test_client()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def login(self, client, username='testuser', password='testpass123'):
        """Helper method to log in a test user."""
        return client.post('/auth/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)
    
    def test_view_cart_authenticated(self, client):
        """Test viewing the cart as an authenticated user."""
        with client:
            self.login(client)
            response = client.get('/cart')
            assert response.status_code == 200
            assert b'Your Cart' in response.data
    
    def test_view_cart_anonymous(self, client):
        """Test viewing the cart as an anonymous user."""
        with client:
            response = client.get('/cart')
            assert response.status_code == 200
            assert b'Your Cart' in response.data
    
    def test_add_to_cart_success(self, client):
        """Test successfully adding an item to the cart."""
        with client:
            self.login(client)
            response = client.post(f'/cart/add/{self.feature_model2.id}', 
                                 headers={'X-Requested-With': 'XMLHttpRequest'})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['message'] == 'Added to cart'
    
    def test_add_to_cart_already_in_cart(self, client):
        """Test adding an item that's already in the cart."""
        with client:
            self.login(client)
            # First add
            client.post(f'/cart/add/{self.feature_model.id}', 
                       headers={'X-Requested-With': 'XMLHttpRequest'})
            # Try to add again
            response = client.post(f'/cart/add/{self.feature_model.id}', 
                                 headers={'X-Requested-With': 'XMLHttpRequest'})
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert 'already in cart' in data['message']
    
    def test_remove_from_cart_success(self, client):
        """Test successfully removing an item from the cart."""
        with client:
            self.login(client)
            # First add an item
            client.post(f'/cart/add/{self.feature_model.id}', 
                       headers={'X-Requested-With': 'XMLHttpRequest'})
            
            # Get the cart item ID
            cart_item = CartItem.query.filter_by(
                cart_id=self.cart.id,
                feature_model_id=self.feature_model.id
            ).first()
            
            # Remove the item
            response = client.delete(f'/cart/remove/{cart_item.id}',
                                   headers={'X-Requested-With': 'XMLHttpRequest'})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['message'] == 'Removed from cart'
    
    def test_remove_from_cart_not_found(self, client):
        """Test removing a non-existent cart item."""
        with client:
            self.login(client)
            response = client.delete('/cart/remove/999',
                                   headers={'X-Requested-With': 'XMLHttpRequest'})
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
    
    def test_clear_cart(self, client):
        """Test clearing the cart."""
        with client:
            self.login(client)
            # Add some items
            client.post(f'/cart/add/{self.feature_model.id}', 
                       headers={'X-Requested-With': 'XMLHttpRequest'})
            client.post(f'/cart/add/{self.feature_model2.id}', 
                       headers={'X-Requested-With': 'XMLHttpRequest'})
            
            # Clear the cart
            response = client.post('/cart/clear',
                                 headers={'X-Requested-With': 'XMLHttpRequest'})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['message'] == 'Cart cleared'
            assert data['cart_count'] == 0
    
    def test_get_cart_count(self, client):
        """Test getting the cart item count."""
        with client:
            self.login(client)
            # Add an item
            client.post(f'/cart/add/{self.feature_model.id}', 
                       headers={'X-Requested-With': 'XMLHttpRequest'})
            
            # Get cart count
            response = client.get('/cart/count',
                                headers={'X-Requested-With': 'XMLHttpRequest'})
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'count' in data
            assert data['count'] > 0
    
    @patch('app.modules.cart.routes.CartService.generate_cart_download')
    def test_download_cart(self, mock_generate, client):
        """Test downloading the cart contents."""
        with client:
            self.login(client)
            # Mock the generate_cart_download method to return a test file
            test_zip_path = '/tmp/test_cart_download.zip'
            with open(test_zip_path, 'w') as f:
                f.write('test content')
            mock_generate.return_value = test_zip_path
            
            # Add an item to the cart
            client.post(f'/cart/add/{self.feature_model.id}', 
                       headers={'X-Requested-With': 'XMLHttpRequest'})
            
            # Download the cart
            response = client.get('/cart/download')
            
            assert response.status_code == 200
            assert response.mimetype == 'application/zip'
            assert 'attachment' in response.headers['Content-Disposition']
    
    def test_download_empty_cart(self, client):
        """Test downloading an empty cart."""
        with client:
            self.login(client)
            # Clear the cart first
            client.post('/cart/clear',
                       headers={'X-Requested-With': 'XMLHttpRequest'})
            
            # Try to download
            response = client.get('/cart/download', follow_redirects=True)
            
            assert b'Your cart is empty' in response.data
