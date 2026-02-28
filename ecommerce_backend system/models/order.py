"""
models/order.py
───────────────
Order model — manages order lifecycle.
"""

from utils.db import execute_query, execute_transaction


class Order:
    """Represents a placed order."""

    VALID_STATUSES = {"pending", "confirmed", "shipped", "delivered", "cancelled"}

    def __init__(self, id=None, user_id=None, total_amount=None,
                 status=None, shipping_address=None, payment_method=None,
                 created_at=None, updated_at=None, items=None):
        self.id               = id
        self.user_id          = user_id
        self.total_amount     = float(total_amount) if total_amount else 0.0
        self.status           = status
        self.shipping_address = shipping_address
        self.payment_method   = payment_method
        self.created_at       = created_at
        self.updated_at       = updated_at
        self.items            = items or []

    def to_dict(self) -> dict:
        return {
            "id":               self.id,
            "user_id":          self.user_id,
            "total_amount":     self.total_amount,
            "status":           self.status,
            "shipping_address": self.shipping_address,
            "payment_method":   self.payment_method,
            "items":            self.items,
            "created_at":       str(self.created_at) if self.created_at else None,
            "updated_at":       str(self.updated_at) if self.updated_at else None,
        }

    # ── DB operations ──────────────────────────────────────────

    @classmethod
    def create_from_cart(cls, user_id: int, cart_items: list,
                         shipping_address: str, payment_method: str = "COD"):
        """
        Atomically:
          1. Insert order
          2. Insert order_items
          3. Decrement product stock
        """
        total = sum(item["price"] * item["quantity"] for item in cart_items)

        queries = [
            (
                """INSERT INTO orders (user_id, total_amount, shipping_address, payment_method)
                   VALUES (%s, %s, %s, %s)""",
                (user_id, total, shipping_address, payment_method)
            )
        ]

        # We need the order_id — use two-phase approach
        import mysql.connector
        from config import config
        from utils.db import get_connection

        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Insert order
            cursor.execute(
                """INSERT INTO orders (user_id, total_amount, shipping_address, payment_method)
                   VALUES (%s, %s, %s, %s)""",
                (user_id, total, shipping_address, payment_method)
            )
            order_id = cursor.lastrowid

            # Insert order items + decrement stock
            for item in cart_items:
                cursor.execute(
                    """INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                       VALUES (%s, %s, %s, %s)""",
                    (order_id, item["product_id"], item["quantity"], item["price"])
                )
                cursor.execute(
                    "UPDATE products SET stock = stock - %s WHERE id = %s",
                    (item["quantity"], item["product_id"])
                )

            conn.commit()
            return order_id

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def find_by_id(cls, order_id: int, user_id: int = None):
        """Fetch order + its items. Optionally scope to a user."""
        condition = "WHERE o.id = %s"
        params    = [order_id]
        if user_id:
            condition += " AND o.user_id = %s"
            params.append(user_id)

        row = execute_query(
            f"SELECT * FROM orders o {condition}", tuple(params), fetch="one"
        )
        if not row:
            return None

        items = execute_query(
            """SELECT oi.*, p.name, p.image_url
               FROM order_items oi
               JOIN products p ON oi.product_id = p.id
               WHERE oi.order_id = %s""",
            (order_id,), fetch="all"
        )

        order = cls(**{k: v for k, v in row.items()})
        order.items = [
            {
                "product_id": i["product_id"],
                "name":       i["name"],
                "quantity":   i["quantity"],
                "unit_price": float(i["unit_price"]),
                "subtotal":   float(i["unit_price"]) * i["quantity"],
                "image_url":  i["image_url"],
            }
            for i in (items or [])
        ]
        return order

    @classmethod
    def get_user_orders(cls, user_id: int, page: int = 1, per_page: int = 10):
        offset = (page - 1) * per_page
        count  = execute_query(
            "SELECT COUNT(*) AS total FROM orders WHERE user_id=%s", (user_id,), fetch="one"
        )
        total = count["total"] if count else 0

        rows = execute_query(
            """SELECT * FROM orders WHERE user_id=%s
               ORDER BY created_at DESC LIMIT %s OFFSET %s""",
            (user_id, per_page, offset), fetch="all"
        )

        orders     = [cls(**r).to_dict() for r in (rows or [])]
        pagination = {
            "total":    total,
            "page":     page,
            "per_page": per_page,
            "pages":    (total + per_page - 1) // per_page,
        }
        return orders, pagination

    @classmethod
    def get_all_orders(cls, page: int = 1, per_page: int = 10, status: str = None):
        """Admin: fetch all orders with optional status filter."""
        offset     = (page - 1) * per_page
        conditions = []
        params     = []
        if status:
            conditions.append("status = %s")
            params.append(status)

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        count = execute_query(
            f"SELECT COUNT(*) AS total FROM orders {where}",
            tuple(params), fetch="one"
        )
        total = count["total"] if count else 0

        rows = execute_query(
            f"""SELECT o.*, u.name AS customer_name, u.email AS customer_email
                FROM orders o JOIN users u ON o.user_id = u.id
                {where}
                ORDER BY o.created_at DESC LIMIT %s OFFSET %s""",
            tuple(params) + (per_page, offset), fetch="all"
        )

        pagination = {
            "total":    total,
            "page":     page,
            "per_page": per_page,
            "pages":    (total + per_page - 1) // per_page,
        }
        return (rows or []), pagination

    @classmethod
    def update_status(cls, order_id: int, status: str) -> bool:
        if status not in cls.VALID_STATUSES:
            return False
        execute_query(
            "UPDATE orders SET status=%s WHERE id=%s", (status, order_id)
        )
        return True
