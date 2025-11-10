import os
import tempfile
from zipfile import ZipFile
from typing import Optional

from flask import session
from flask_login import current_user

from app.modules.cart.models import Cart, CartItem
from app.modules.cart.repositories import CartRepository
from app.modules.featuremodel.models import FeatureModel
from app.modules.dataset.models import DSDownloadRecord, DataSet
from app import db
from datetime import datetime, timezone
import uuid


class CartService:
    """Service for cart business logic."""

    def __init__(self):
        self.repository = CartRepository()

    def get_or_create_cart(self) -> Cart:
        """
        Get or create a cart for the current user.
        Uses user_id if authenticated, otherwise uses session_id.
        """
        if current_user.is_authenticated:
            return self.repository.get_or_create_for_user(current_user.id)
        else:
            # For anonymous users, use session ID
            if 'cart_session_id' not in session:
                session['cart_session_id'] = str(uuid.uuid4())
            return self.repository.get_or_create_for_session(session['cart_session_id'])

    def add_to_cart(self, feature_model_id: int) -> dict:
        """Add a feature model to the cart."""
        cart = self.get_or_create_cart()

        # Check if feature model exists
        feature_model = FeatureModel.query.get(feature_model_id)
        if not feature_model:
            return {'success': False, 'message': 'Feature model not found'}

        # Check if already in cart
        if self.repository.item_exists(cart, feature_model_id):
            return {'success': False, 'message': 'Item already in cart'}

        # Add to cart
        cart_item = self.repository.add_item(cart, feature_model_id)

        return {
            'success': True,
            'message': 'Added to cart',
            'cart_item_id': cart_item.id,
            'cart_count': self.get_cart_count()
        }

    def remove_from_cart(self, cart_item_id: int) -> dict:
        """Remove an item from the cart."""
        cart_item = CartItem.query.get(cart_item_id)

        if not cart_item:
            return {'success': False, 'message': 'Item not found'}

        # Verify ownership
        cart = self.get_or_create_cart()
        if cart_item.cart_id != cart.id:
            return {'success': False, 'message': 'Unauthorized'}

        success = self.repository.remove_item(cart_item_id)

        return {
            'success': success,
            'message': 'Removed from cart' if success else 'Failed to remove',
            'cart_count': self.get_cart_count()
        }

    def clear_cart(self) -> dict:
        """Clear all items from the cart."""
        cart = self.get_or_create_cart()
        self.repository.clear_cart(cart)

        return {
            'success': True,
            'message': 'Cart cleared',
            'cart_count': 0
        }

    def get_cart_items(self) -> list:
        """Get all items in the current user's cart with details."""
        cart = self.get_or_create_cart()
        return self.repository.get_cart_with_details(cart)

    def get_cart_count(self) -> int:
        """Get the number of items in the current user's cart."""
        cart = self.get_or_create_cart()
        return self.repository.get_item_count(cart)

    def merge_session_cart_on_login(self, user_id: int) -> None:
        """
        Merge anonymous cart into user cart when user logs in.
        Should be called after successful login.
        """
        if 'cart_session_id' in session:
            session_cart = self.repository.get_by_session_id(session['cart_session_id'])
            if session_cart:
                user_cart = self.repository.get_or_create_for_user(user_id)
                self.repository.merge_carts(session_cart, user_cart)
                # Clear session cart ID
                session.pop('cart_session_id', None)

    def generate_cart_download(self) -> Optional[str]:
        """
        Generate a ZIP file containing all feature models in the cart.
        Returns the path to the generated ZIP file.
        """
        cart = self.get_or_create_cart()
        cart_items = self.repository.get_cart_items(cart)

        if not cart_items:
            return None

        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        zip_filename = f"my_custom_dataset_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)

        # Create ZIP file
        with ZipFile(zip_path, 'w') as zipf:
            # Track datasets for README
            datasets_info = {}

            for cart_item in cart_items:
                feature_model = cart_item.feature_model

                if not feature_model:
                    continue

                # Get dataset information
                dataset = DataSet.query.get(feature_model.data_set_id)
                if not dataset:
                    continue

                dataset_name = dataset.ds_meta_data.title if dataset.ds_meta_data else f"dataset_{dataset.id}"
                dataset_name = self._sanitize_filename(dataset_name)

                # Track dataset info for README
                if dataset.id not in datasets_info:
                    datasets_info[dataset.id] = {
                        'name': dataset_name,
                        'models': []
                    }

                # Add feature model files to ZIP
                for hubfile in feature_model.files:
                    file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/{hubfile.name}"

                    if os.path.exists(file_path):
                        # Create structure: dataset_name/model_file.uvl
                        arcname = os.path.join(dataset_name, hubfile.name)
                        zipf.write(file_path, arcname=arcname)

                        # Track for README
                        datasets_info[dataset.id]['models'].append(hubfile.name)

            # Add README file
            readme_content = self._generate_readme(datasets_info)
            readme_path = os.path.join(temp_dir, 'README.txt')
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            zipf.write(readme_path, arcname='README.txt')

        # Record download for each feature model
        self._record_downloads(cart_items)

        return zip_path

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to be filesystem-safe."""
        import re
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        return filename[:100]

    def _generate_readme(self, datasets_info: dict) -> str:
        """Generate README content for the cart download."""
        content = [
            "=" * 60,
            "CUSTOM DATASET - UVLHUB.IO",
            "=" * 60,
            "",
            f"Downloaded: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "This archive contains feature models you selected from UVLHUB.IO",
            "",
            "=" * 60,
            "CONTENTS",
            "=" * 60,
            ""
        ]

        for dataset_id, info in datasets_info.items():
            content.append(f"Dataset: {info['name']}")
            content.append(f"  Models ({len(info['models'])}):")
            for model in info['models']:
                content.append(f"    - {model}")
            content.append("")

        content.extend([
            "=" * 60,
            "CITATION",
            "=" * 60,
            "",
            "If you use these models in your research, please cite:",
            "UVLHUB.IO - https://uvlhub.io",
            "",
            "For individual dataset citations, please refer to the",
            "original dataset pages on UVLHUB.IO",
            ""
        ])

        return "\n".join(content)

    def _record_downloads(self, cart_items: list) -> None:
        """Record download statistics for cart items."""
        user_id = current_user.id if current_user.is_authenticated else None
        download_cookie = session.get('download_cookie', str(uuid.uuid4()))

        # Ensure cookie is saved
        if 'download_cookie' not in session:
            session['download_cookie'] = download_cookie

        for cart_item in cart_items:
            feature_model = cart_item.feature_model
            if feature_model:
                dataset_id = feature_model.data_set_id

                # Create download record
                download_record = DSDownloadRecord(
                    user_id=user_id,
                    dataset_id=dataset_id,
                    download_date=datetime.now(timezone.utc),
                    download_cookie=download_cookie
                )
                db.session.add(download_record)

        db.session.commit()
