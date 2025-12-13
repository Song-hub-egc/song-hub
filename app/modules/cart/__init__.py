from flask import Blueprint

cart_bp = Blueprint("cart", __name__, template_folder="templates")

from app.modules.cart import routes  # noqa: E402, F401
