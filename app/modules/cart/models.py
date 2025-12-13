from datetime import datetime, timezone

from app import db


class Cart(db.Model):
    """
    Shopping cart for feature models.
    Can be associated with a user (authenticated) or a session (anonymous).
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    session_id = db.Column(db.String(255), nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', backref='cart', uselist=False)
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        if self.user_id:
            return f'<Cart user_id={self.user_id} items={len(self.items)}>'
        return f'<Cart session_id={self.session_id} items={len(self.items)}>'

    def get_item_count(self):
        """Get the number of items in the cart."""
        return len(self.items)

    def is_empty(self):
        """Check if the cart is empty."""
        return len(self.items) == 0

    def clear(self):
        """Remove all items from the cart."""
        for item in self.items:
            db.session.delete(item)

    def has_feature_model(self, feature_model_id):
        """Check if a feature model is already in the cart."""
        return any(item.feature_model_id == feature_model_id for item in self.items)


class CartItem(db.Model):
    """
    Individual item in a shopping cart.
    Each item represents a feature model selected by the user.
    """
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    feature_model_id = db.Column(db.Integer, db.ForeignKey('feature_model.id'), nullable=False)
    added_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    feature_model = db.relationship('FeatureModel', backref='cart_items', lazy=True)

    def __repr__(self):
        return f'<CartItem cart_id={self.cart_id} feature_model_id={self.feature_model_id}>'
