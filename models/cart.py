"""
models/cart.py
──────────────
Cart model — manages a user's shopping cart.
"""

from utils.db import execute_query


class Cart:
    """Represents the shopping cart layer."""

    @staticmethod
    def get_user_cart(user_id: int) -> dict:
        """Return all cart items + running total for a user."""
        rows = execute_query(
            """SELECT c.id, c.quantity, c.added_at,
                      p.id AS product_id, p.name, p.price,
                      p.image_url, p.stock,
                      (c.quantity * p.price) AS subtotal
               FROM cart c
               JOIN products p ON c.product_id = p.id
               WHERE c.user_id = %s""",
            (user_id,), fetch="all"
        )

        items = []
        total = 0.0
        for r in (rows or []):
            item = {
                "cart_item_id": r["id"],
                "product_id":   r["product_id"],
                "name":         r["name"],
                "price":        float(r["price"]),
                "quantity":     r["quantity"],
                "subtotal":     float(r["subtotal"]),
                "image_url":    r["image_url"],
                "in_stock":     r["stock"] >= r["quantity"],
            }
            items.append(item)
            total += float(r["subtotal"])

        return {"items": items, "total": round(total, 2), "item_count": len(items)}

    @staticmethod
    def add_item(user_id: int, product_id: int, quantity: int = 1):
        """Add item or increment quantity if already in cart."""
        existing = execute_query(
            "SELECT id, quantity FROM cart WHERE user_id=%s AND product_id=%s",
            (user_id, product_id), fetch="one"
        )
        if existing:
            execute_query(
                "UPDATE cart SET quantity = quantity + %s WHERE user_id=%s AND product_id=%s",
                (quantity, user_id, product_id)
            )
        else:
            execute_query(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                (user_id, product_id, quantity)
            )

    @staticmethod
    def update_quantity(user_id: int, product_id: int, quantity: int):
        """Set an exact quantity. Pass 0 to remove."""
        if quantity <= 0:
            Cart.remove_item(user_id, product_id)
        else:
            execute_query(
                "UPDATE cart SET quantity=%s WHERE user_id=%s AND product_id=%s",
                (quantity, user_id, product_id)
            )

    @staticmethod
    def remove_item(user_id: int, product_id: int):
        execute_query(
            "DELETE FROM cart WHERE user_id=%s AND product_id=%s",
            (user_id, product_id)
        )

    @staticmethod
    def clear(user_id: int):
        execute_query("DELETE FROM cart WHERE user_id=%s", (user_id,))

    @staticmethod
    def item_count(user_id: int) -> int:
        row = execute_query(
            "SELECT SUM(quantity) AS total FROM cart WHERE user_id=%s",
            (user_id,), fetch="one"
        )
        return int(row["total"] or 0) if row else 0
