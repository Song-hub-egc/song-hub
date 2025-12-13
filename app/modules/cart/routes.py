import logging
import os

from flask import jsonify, render_template, send_file, flash, redirect, url_for, request
from flask_login import login_required, current_user

from app.modules.cart import cart_bp
from app.modules.cart.services import CartService

logger = logging.getLogger(__name__)

cart_service = CartService()


@cart_bp.route('/cart', methods=['GET'])
def view_cart():
    """View the shopping cart page."""
    cart_items = cart_service.get_cart_items()
    cart_count = len(cart_items)

    return render_template(
        'cart/index.html',
        cart_items=cart_items,
        cart_count=cart_count
    )


@cart_bp.route('/cart/add/<int:feature_model_id>', methods=['POST'])
def add_to_cart(feature_model_id):
    """Add a feature model to the cart (AJAX endpoint)."""
    try:
        result = cart_service.add_to_cart(feature_model_id)
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    except Exception as e:
        logger.exception(f"Error adding to cart: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500


@cart_bp.route('/cart/remove/<int:cart_item_id>', methods=['DELETE', 'POST'])
def remove_from_cart(cart_item_id):
    """Remove an item from the cart (AJAX endpoint)."""
    try:
        result = cart_service.remove_from_cart(cart_item_id)
        # Handle POST method (for form submission fallback if needed)
        if request.method == 'POST':
             if result['success']:
                 flash('Item removed from cart', 'success')
             else:
                 flash(result['message'], 'error')
             return redirect(url_for('cart.view_cart'))
             
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    except Exception as e:
        logger.exception(f"Error removing from cart: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500


@cart_bp.route('/cart/clear', methods=['POST'])
def clear_cart():
    """Clear all items from the cart."""
    try:
        result = cart_service.clear_cart()
        return jsonify(result), 200
    except Exception as e:
        logger.exception(f"Error clearing cart: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500


@cart_bp.route('/cart/count', methods=['GET'])
def get_cart_count():
    """Get the number of items in the cart (AJAX endpoint)."""
    try:
        count = cart_service.get_cart_count()
        return jsonify({'count': count}), 200
    except Exception as e:
        logger.exception(f"Error getting cart count: {e}")
        return jsonify({'count': 0}), 500


@cart_bp.route('/cart/download', methods=['GET'])
def download_cart():
    """Download all feature models in the cart as a ZIP file."""
    try:
        cart_count = cart_service.get_cart_count()

        if cart_count == 0:
            flash('Your cart is empty. Add some models first!', 'warning')
            return redirect(url_for('cart.view_cart'))

        # Generate ZIP file
        zip_path = cart_service.generate_cart_download()

        if not zip_path or not os.path.exists(zip_path):
            flash('Failed to generate download. Please try again.', 'error')
            return redirect(url_for('cart.view_cart'))

        # Send file
        zip_filename = os.path.basename(zip_path)

        return send_file(
            zip_path,
            as_attachment=True,
            download_name=zip_filename,
            mimetype='application/zip'
        )

    except Exception as e:
        logger.exception(f"Error downloading cart: {e}")
        flash('An error occurred while generating your download.', 'error')
        return redirect(url_for('cart.view_cart'))
