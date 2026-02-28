"""
routes/cart_routes.py
─────────────────────
Cart endpoints (all require auth):
  GET    /cart
  POST   /cart
  PUT    /cart/<product_id>
  DELETE /cart/<product_id>
  DELETE /cart
"""

from flask import Blueprint, request
from services.cart_service import CartService
from utils.jwt_handler     import token_required
from utils.response        import success, error

cart_bp = Blueprint("cart", __name__, url_prefix="/cart")


@cart_bp.route("/", methods=["GET"])
@token_required
def get_cart(current_user):
    """Get the logged-in user's cart."""
    try:
        cart = CartService.get_cart(current_user["id"])
        return success("Cart fetched", cart)
    except Exception as e:
        return error(str(e), 500)


@cart_bp.route("/", methods=["POST"])
@token_required
def add_to_cart(current_user):
    """Add a product to cart (or increment quantity)."""
    data = request.get_json() or {}
    try:
        cart = CartService.add_to_cart(
            user_id    = current_user["id"],
            product_id = int(data.get("product_id", 0)),
            quantity   = int(data.get("quantity", 1))
        )
        return success("Item added to cart", cart, status=201)
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(str(e), 500)


@cart_bp.route("/<int:product_id>", methods=["PUT"])
@token_required
def update_cart_item(current_user, product_id):
    """Update quantity of a cart item (set to 0 to remove)."""
    data = request.get_json() or {}
    try:
        cart = CartService.update_item(
            user_id    = current_user["id"],
            product_id = product_id,
            quantity   = int(data.get("quantity", 1))
        )
        return success("Cart updated", cart)
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(str(e), 500)


@cart_bp.route("/<int:product_id>", methods=["DELETE"])
@token_required
def remove_from_cart(current_user, product_id):
    """Remove a specific item from cart."""
    try:
        cart = CartService.remove_from_cart(current_user["id"], product_id)
        return success("Item removed from cart", cart)
    except Exception as e:
        return error(str(e), 500)


@cart_bp.route("/", methods=["DELETE"])
@token_required
def clear_cart(current_user):
    """Empty the entire cart."""
    try:
        CartService.clear_cart(current_user["id"])
        return success("Cart cleared")
    except Exception as e:
        return error(str(e), 500)
