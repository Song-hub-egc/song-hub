from datetime import datetime, timezone
from typing import Optional

from app import db
from app.modules.cart.models import Cart, CartItem


class CartRepository:
    """Repository for cart database operations."""

    def get_by_user_id(self, user_id: int) -> Optional[Cart]:
        """Get cart by user ID."""
        return Cart.query.filter_by(user_id=user_id).first()

    def get_by_session_id(self, session_id: str) -> Optional[Cart]:
        """Get cart by session ID."""
        return Cart.query.filter_by(session_id=session_id).first()

    def get_or_create_for_user(self, user_id: int) -> Cart:
        """Get or create a cart for an authenticated user."""
        cart = self.get_by_user_id(user_id)
        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.commit()
        return cart

    def get_or_create_for_session(self, session_id: str) -> Cart:
        """Get or create a cart for an anonymous user (by session)."""
        cart = self.get_by_session_id(session_id)
        if not cart:
            cart = Cart(session_id=session_id)
            db.session.add(cart)
            db.session.commit()
        return cart

    def add_item(self, cart: Cart, feature_model_id: Optional[int] = None, audio_id: Optional[int] = None) -> CartItem:
        """Add a feature model or audio to the cart."""
        if feature_model_id:
            # Check if item already exists
            existing_item = CartItem.query.filter_by(cart_id=cart.id, feature_model_id=feature_model_id).first()
        elif audio_id:
            existing_item = CartItem.query.filter_by(cart_id=cart.id, audio_id=audio_id).first()
        else:
            raise ValueError("Either feature_model_id or audio_id must be provided")

        if existing_item:
            return existing_item

        # Create new cart item
        cart_item = CartItem(cart_id=cart.id, feature_model_id=feature_model_id, audio_id=audio_id)
        db.session.add(cart_item)

        # Update cart timestamp
        cart.updated_at = datetime.now(timezone.utc)

        db.session.commit()
        return cart_item

    def remove_item(self, cart_item_id: int) -> bool:
        """Remove an item from the cart."""
        cart_item = CartItem.query.get(cart_item_id)
        if cart_item:
            cart = cart_item.cart
            db.session.delete(cart_item)
            cart.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            return True
        return False

    def remove_item_by_feature_model(self, cart: Cart, feature_model_id: int) -> bool:
        """Remove an item from the cart by feature model ID."""
        cart_item = CartItem.query.filter_by(cart_id=cart.id, feature_model_id=feature_model_id).first()

        if cart_item:
            db.session.delete(cart_item)
            cart.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            return True
        return False

    def remove_item_by_audio(self, cart: Cart, audio_id: int) -> bool:
        """Remove an item from the cart by audio ID."""
        cart_item = CartItem.query.filter_by(cart_id=cart.id, audio_id=audio_id).first()

        if cart_item:
            db.session.delete(cart_item)
            cart.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            return True
        return False

    def clear_cart(self, cart: Cart) -> None:
        """Remove all items from a cart."""
        CartItem.query.filter_by(cart_id=cart.id).delete()
        cart.updated_at = datetime.now(timezone.utc)
        db.session.commit()

    def get_cart_items(self, cart: Cart) -> list:
        """Get all items in a cart with their feature models."""
        return CartItem.query.filter_by(cart_id=cart.id).all()

    def get_item_count(self, cart: Cart) -> int:
        """Get the number of items in a cart."""
        return CartItem.query.filter_by(cart_id=cart.id).count()

    def item_exists(self, cart: Cart, feature_model_id: Optional[int] = None, audio_id: Optional[int] = None) -> bool:
        """Check if a feature model or audio is already in the cart."""
        if feature_model_id:
            return CartItem.query.filter_by(cart_id=cart.id, feature_model_id=feature_model_id).first() is not None
        elif audio_id:
            return CartItem.query.filter_by(cart_id=cart.id, audio_id=audio_id).first() is not None
        return False

    def merge_carts(self, session_cart: Cart, user_cart: Cart) -> None:
        """Merge session cart into user cart when user logs in."""
        # Get all items from session cart
        session_items = self.get_cart_items(session_cart)

        for session_item in session_items:
            # Add to user cart if not already there
            if session_item.feature_model_id:
                if not self.item_exists(user_cart, feature_model_id=session_item.feature_model_id):
                    self.add_item(user_cart, feature_model_id=session_item.feature_model_id)
            elif session_item.audio_id:
                if not self.item_exists(user_cart, audio_id=session_item.audio_id):
                    self.add_item(user_cart, audio_id=session_item.audio_id)

        # Delete session cart
        db.session.delete(session_cart)
        db.session.commit()

    def get_cart_with_details(self, cart: Cart) -> list:
        """Get cart items with full feature model/audio and dataset details."""
        items = []
        for cart_item in cart.items:
            if cart_item.feature_model_id:
                feature_model = cart_item.feature_model
                if feature_model and feature_model.fm_meta_data:
                    dataset = feature_model.data_set if hasattr(feature_model, "data_set") else None
                    items.append(
                        {
                            "cart_item_id": cart_item.id,
                            "id": feature_model.id,
                            "type": "feature_model",
                            "title": feature_model.fm_meta_data.title,
                            "description": feature_model.fm_meta_data.description,
                            "dataset": dataset,
                            "added_at": cart_item.added_at,
                            "feature_model": feature_model,
                        }
                    )
            elif cart_item.audio_id:
                audio = cart_item.audio
                if audio and audio.audio_meta_data:
                    dataset = audio.data_set if hasattr(audio, "data_set") else None

                    items.append(
                        {
                            "cart_item_id": cart_item.id,
                            "id": audio.id,
                            "type": "audio",
                            "title": audio.audio_meta_data.title,
                            "description": audio.audio_meta_data.description,
                            "dataset": audio.audio_dataset,
                            "added_at": cart_item.added_at,
                            "audio": audio,
                        }
                    )
        return items
