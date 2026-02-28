"""
models/product.py
─────────────────
Product model — OOP representation with DB operations and pagination.
"""

from utils.db import execute_query
from config import config


class Product:
    """Represents a product in the catalogue."""

    def __init__(self, id=None, name=None, description=None,
                 price=None, stock=None, category_id=None,
                 image_url=None, is_active=True, created_at=None,
                 updated_at=None, category_name=None):
        self.id            = id
        self.name          = name
        self.description   = description
        self.price         = float(price) if price else 0.0
        self.stock         = stock
        self.category_id   = category_id
        self.category_name = category_name   # joined field
        self.image_url     = image_url
        self.is_active     = is_active
        self.created_at    = created_at
        self.updated_at    = updated_at

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "name":          self.name,
            "description":   self.description,
            "price":         self.price,
            "stock":         self.stock,
            "category_id":   self.category_id,
            "category_name": self.category_name,
            "image_url":     self.image_url,
            "is_active":     self.is_active,
            "in_stock":      self.stock > 0,
            "created_at":    str(self.created_at) if self.created_at else None,
        }

    # ── CRUD ───────────────────────────────────────────────────

    @classmethod
    def find_by_id(cls, product_id: int):
        row = execute_query(
            """SELECT p.*, c.name AS category_name
               FROM products p
               LEFT JOIN categories c ON p.category_id = c.id
               WHERE p.id = %s AND p.is_active = TRUE""",
            (product_id,), fetch="one"
        )
        return cls(**row) if row else None

    @classmethod
    def get_all(cls, page: int = 1, per_page: int = None,
                category_id: int = None, search: str = None,
                min_price: float = None, max_price: float = None,
                sort_by: str = "created_at", order: str = "DESC"):
        """Paginated product listing with filters."""
        per_page = per_page or config.DEFAULT_PAGE_SIZE
        offset   = (page - 1) * per_page

        # Whitelist sortable columns to prevent SQL injection
        ALLOWED_SORT = {"price", "name", "created_at", "stock"}
        if sort_by not in ALLOWED_SORT:
            sort_by = "created_at"
        order = "ASC" if order.upper() == "ASC" else "DESC"

        conditions = ["p.is_active = TRUE"]
        params     = []

        if category_id:
            conditions.append("p.category_id = %s")
            params.append(category_id)
        if search:
            conditions.append("MATCH(p.name, p.description) AGAINST (%s IN BOOLEAN MODE)")
            params.append(f"{search}*")
        if min_price is not None:
            conditions.append("p.price >= %s")
            params.append(min_price)
        if max_price is not None:
            conditions.append("p.price <= %s")
            params.append(max_price)

        where = "WHERE " + " AND ".join(conditions)

        # Count
        count_row = execute_query(
            f"SELECT COUNT(*) AS total FROM products p {where}",
            tuple(params), fetch="one"
        )
        total = count_row["total"] if count_row else 0

        # Fetch page
        rows = execute_query(
            f"""SELECT p.*, c.name AS category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                {where}
                ORDER BY p.{sort_by} {order}
                LIMIT %s OFFSET %s""",
            tuple(params) + (per_page, offset), fetch="all"
        )

        products = [cls(**r).to_dict() for r in (rows or [])]

        pagination = {
            "total":    total,
            "page":     page,
            "per_page": per_page,
            "pages":    (total + per_page - 1) // per_page,
        }
        return products, pagination

    @classmethod
    def create(cls, name, description, price, stock, category_id, image_url=None):
        result = execute_query(
            """INSERT INTO products (name, description, price, stock, category_id, image_url)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (name, description, price, stock, category_id, image_url)
        )
        return result["lastrowid"]

    @classmethod
    def update(cls, product_id, **fields):
        allowed = {"name", "description", "price", "stock", "category_id",
                   "image_url", "is_active"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return False
        set_clause = ", ".join(f"{k} = %s" for k in updates)
        execute_query(
            f"UPDATE products SET {set_clause} WHERE id = %s",
            tuple(updates.values()) + (product_id,)
        )
        return True

    @classmethod
    def decrement_stock(cls, product_id: int, qty: int):
        execute_query(
            "UPDATE products SET stock = stock - %s WHERE id = %s AND stock >= %s",
            (qty, product_id, qty)
        )

    @classmethod
    def get_categories(cls):
        return execute_query("SELECT * FROM categories ORDER BY name", fetch="all")
