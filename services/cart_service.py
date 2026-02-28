"""
services/cart_service.py
────────────────────────
Cart business logic — add, update, remove, clear.
"""

from models.cart    import Cart
from models.product import Product


class CartService:
    """Manages shopping cart operations."""

    @staticmethod
    def get_cart(user_id: int) -> dict:
        return Cart.get_user_cart(user_id)

    @staticmethod
    def add_to_cart(user_id: int, product_id: int, quantity: int = 1) -> dict:
        if quantity < 1:
            raise ValueError("Quantity must be at least 1")

        product = Product.find_by_id(product_id)
        if not product:
            raise ValueError("Product not found or unavailable")
        if product.stock < quantity:
            raise ValueError(f"Only {product.stock} units available in stock")

        Cart.add_item(user_id, product_id, quantity)
        return Cart.get_user_cart(user_id)

    @staticmethod
    def update_item(user_id: int, product_id: int, quantity: int) -> dict:
        product = Product.find_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        if quantity > 0 and product.stock < quantity:
            raise ValueError(f"Only {product.stock} units available in stock")

        Cart.update_quantity(user_id, product_id, quantity)
        return Cart.get_user_cart(user_id)

    @staticmethod
    def remove_from_cart(user_id: int, product_id: int) -> dict:
        Cart.remove_item(user_id, product_id)
        return Cart.get_user_cart(user_id)

    @staticmethod
    def clear_cart(user_id: int):
        Cart.clear(user_id)
