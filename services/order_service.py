"""
services/order_service.py
─────────────────────────
Order business logic — place order, track, admin management.
"""

from models.order   import Order
from models.cart    import Cart
from models.product import Product


class OrderService:
    """Handles order placement and lifecycle management."""

    @staticmethod
    def place_order(user_id: int, shipping_address: str,
                    payment_method: str = "COD") -> dict:
        """
        Convert the user's cart into a confirmed order.
        Validates stock, creates order atomically, clears cart.
        """
        if not shipping_address or not shipping_address.strip():
            raise ValueError("Shipping address is required")

        cart = Cart.get_user_cart(user_id)
        if not cart["items"]:
            raise ValueError("Your cart is empty")

        # Validate stock for every item before placing
        for item in cart["items"]:
            product = Product.find_by_id(item["product_id"])
            if not product:
                raise ValueError(f"Product '{item['name']}' is no longer available")
            if product.stock < item["quantity"]:
                raise ValueError(
                    f"Insufficient stock for '{item['name']}'. "
                    f"Available: {product.stock}, requested: {item['quantity']}"
                )

        order_id = Order.create_from_cart(
            user_id          = user_id,
            cart_items       = cart["items"],
            shipping_address = shipping_address.strip(),
            payment_method   = payment_method
        )

        # Clear cart after successful order
        Cart.clear(user_id)

        return Order.find_by_id(order_id).to_dict()

    @staticmethod
    def get_order(order_id: int, user_id: int = None) -> dict:
        """Fetch an order. Pass user_id to scope to that customer."""
        order = Order.find_by_id(order_id, user_id)
        if not order:
            raise ValueError("Order not found")
        return order.to_dict()

    @staticmethod
    def get_user_orders(user_id: int, page: int = 1, per_page: int = 10):
        return Order.get_user_orders(user_id, page, per_page)

    @staticmethod
    def cancel_order(order_id: int, user_id: int) -> dict:
        order = Order.find_by_id(order_id, user_id)
        if not order:
            raise ValueError("Order not found")
        if order.status not in ("pending", "confirmed"):
            raise ValueError(f"Cannot cancel an order with status '{order.status}'")

        Order.update_status(order_id, "cancelled")
        return Order.find_by_id(order_id).to_dict()

    # ── Admin ──────────────────────────────────────────────────

    @staticmethod
    def get_all_orders(page: int = 1, per_page: int = 10, status: str = None):
        rows, pagination = Order.get_all_orders(page, per_page, status)
        orders = [
            {
                "id":               r["id"],
                "user_id":          r["user_id"],
                "customer_name":    r.get("customer_name"),
                "customer_email":   r.get("customer_email"),
                "total_amount":     float(r["total_amount"]),
                "status":           r["status"],
                "payment_method":   r["payment_method"],
                "created_at":       str(r["created_at"]),
            }
            for r in rows
        ]
        return orders, pagination

    @staticmethod
    def update_order_status(order_id: int, status: str) -> dict:
        if status not in Order.VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(Order.VALID_STATUSES)}")
        if not Order.update_status(order_id, status):
            raise ValueError("Order not found")
        return Order.find_by_id(order_id).to_dict()
