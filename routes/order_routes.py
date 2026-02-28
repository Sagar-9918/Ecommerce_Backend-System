"""
routes/order_routes.py
──────────────────────
Order endpoints:
  POST /orders                    – place order from cart
  GET  /orders                    – my orders
  GET  /orders/<id>               – single order
  PUT  /orders/<id>/cancel        – cancel order

  GET  /orders/admin              – all orders [admin]
  PUT  /orders/admin/<id>/status  – update status [admin]
"""

from flask import Blueprint, request
from services.order_service import OrderService
from utils.jwt_handler      import token_required, admin_required
from utils.response         import success, error

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")


@orders_bp.route("/", methods=["POST"])
@token_required
def place_order(current_user):
    """Place an order from the current cart."""
    data = request.get_json() or {}
    try:
        order = OrderService.place_order(
            user_id          = current_user["id"],
            shipping_address = data.get("shipping_address", ""),
            payment_method   = data.get("payment_method", "COD")
        )
        return success("Order placed successfully", order, status=201)
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(f"Failed to place order: {e}", 500)


@orders_bp.route("/", methods=["GET"])
@token_required
def get_my_orders(current_user):
    """Fetch the logged-in user's order history."""
    page     = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    try:
        orders, pagination = OrderService.get_user_orders(
            current_user["id"], page, per_page
        )
        return success("Orders fetched", orders, pagination=pagination)
    except Exception as e:
        return error(str(e), 500)


@orders_bp.route("/<int:order_id>", methods=["GET"])
@token_required
def get_order(current_user, order_id):
    """Get details of a specific order (must belong to user)."""
    try:
        order = OrderService.get_order(order_id, current_user["id"])
        return success("Order fetched", order)
    except ValueError as e:
        return error(str(e), 404)
    except Exception as e:
        return error(str(e), 500)


@orders_bp.route("/<int:order_id>/cancel", methods=["PUT"])
@token_required
def cancel_order(current_user, order_id):
    """Cancel a pending or confirmed order."""
    try:
        order = OrderService.cancel_order(order_id, current_user["id"])
        return success("Order cancelled", order)
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(str(e), 500)


# ── Admin endpoints ────────────────────────────────────────────

@orders_bp.route("/admin", methods=["GET"])
@admin_required
def admin_get_orders(current_user):
    """Admin — view all orders with optional status filter."""
    page     = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    status   = request.args.get("status")
    try:
        orders, pagination = OrderService.get_all_orders(page, per_page, status)
        return success("All orders fetched", orders, pagination=pagination)
    except Exception as e:
        return error(str(e), 500)


@orders_bp.route("/admin/<int:order_id>/status", methods=["PUT"])
@admin_required
def admin_update_status(current_user, order_id):
    """Admin — update order status (confirmed/shipped/delivered/cancelled)."""
    data = request.get_json() or {}
    try:
        order = OrderService.update_order_status(order_id, data.get("status", ""))
        return success("Order status updated", order)
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(str(e), 500)
