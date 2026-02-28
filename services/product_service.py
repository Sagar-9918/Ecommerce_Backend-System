"""
services/product_service.py
────────────────────────────
Product business logic — catalogue, search, admin CRUD.
"""

from models.product import Product


class ProductService:
    """All product-related business operations."""

    @staticmethod
    def get_products(page=1, per_page=10, category_id=None,
                     search=None, min_price=None, max_price=None,
                     sort_by="created_at", order="DESC"):

        if page < 1:
            page = 1
        if per_page > 100:
            per_page = 100

        products, pagination = Product.get_all(
            page=page, per_page=per_page,
            category_id=category_id, search=search,
            min_price=min_price, max_price=max_price,
            sort_by=sort_by, order=order
        )
        return products, pagination

    @staticmethod
    def get_product(product_id: int) -> dict:
        product = Product.find_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        return product.to_dict()

    @staticmethod
    def get_categories() -> list:
        rows = Product.get_categories()
        return rows or []

    # ── Admin operations ───────────────────────────────────────

    @staticmethod
    def create_product(name, description, price, stock, category_id, image_url=None):
        if not name or not name.strip():
            raise ValueError("Product name is required")
        if price is None or float(price) < 0:
            raise ValueError("Price must be a non-negative number")
        if stock is None or int(stock) < 0:
            raise ValueError("Stock must be a non-negative integer")

        product_id = Product.create(
            name=name.strip(),
            description=description,
            price=float(price),
            stock=int(stock),
            category_id=category_id,
            image_url=image_url
        )
        return Product.find_by_id(product_id).to_dict()

    @staticmethod
    def update_product(product_id: int, **fields):
        product = Product.find_by_id(product_id)
        if not product:
            raise ValueError("Product not found")

        Product.update(product_id, **fields)
        return Product.find_by_id(product_id).to_dict()

    @staticmethod
    def delete_product(product_id: int):
        """Soft delete — set is_active = False."""
        product = Product.find_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        Product.update(product_id, is_active=False)
