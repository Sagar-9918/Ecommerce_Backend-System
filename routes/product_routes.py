"""
routes/product_routes.py
────────────────────────
Product endpoints:
  GET    /products             – list with filters & pagination
  GET    /products/<id>        – single product
  GET    /products/categories  – all categories
  POST   /products             – create  [admin]
  PUT    /products/<id>        – update  [admin]
  DELETE /products/<id>        – soft-delete [admin]
"""

from flask import Blueprint, request
from services.product_service import ProductService
from utils.jwt_handler        import token_required, admin_required
from utils.response           import success, error

products_bp = Blueprint("products", __name__, url_prefix="/products")


@products_bp.route("/", methods=["GET"])
def get_products():
    """Public — paginated product catalogue with optional filters."""
    try:
        page        = int(request.args.get("page", 1))
        per_page    = int(request.args.get("per_page", 10))
        category_id = request.args.get("category_id", type=int)
        search      = request.args.get("search", "")
        min_price   = request.args.get("min_price", type=float)
        max_price   = request.args.get("max_price", type=float)
        sort_by     = request.args.get("sort_by", "created_at")
        order       = request.args.get("order", "DESC")

        products, pagination = ProductService.get_products(
            page=page, per_page=per_page,
            category_id=category_id, search=search or None,
            min_price=min_price, max_price=max_price,
            sort_by=sort_by, order=order
        )
        return success("Products fetched", products, pagination=pagination)
    except Exception as e:
        return error(f"Failed to fetch products: {e}", 500)


@products_bp.route("/categories", methods=["GET"])
def get_categories():
    """Public — all product categories."""
    try:
        categories = ProductService.get_categories()
        return success("Categories fetched", categories)
    except Exception as e:
        return error(str(e), 500)


@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Public — single product details."""
    try:
        product = ProductService.get_product(product_id)
        return success("Product fetched", product)
    except ValueError as e:
        return error(str(e), 404)
    except Exception as e:
        return error(str(e), 500)


@products_bp.route("/", methods=["POST"])
@admin_required
def create_product(current_user):
    """Admin — create a new product."""
    data = request.get_json() or {}
    try:
        product = ProductService.create_product(
            name        = data.get("name"),
            description = data.get("description"),
            price       = data.get("price"),
            stock       = data.get("stock", 0),
            category_id = data.get("category_id"),
            image_url   = data.get("image_url")
        )
        return success("Product created", product, status=201)
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(str(e), 500)


@products_bp.route("/<int:product_id>", methods=["PUT"])
@admin_required
def update_product(current_user, product_id):
    """Admin — update a product."""
    data = request.get_json() or {}
    try:
        product = ProductService.update_product(product_id, **data)
        return success("Product updated", product)
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(str(e), 500)


@products_bp.route("/<int:product_id>", methods=["DELETE"])
@admin_required
def delete_product(current_user, product_id):
    """Admin — soft-delete a product."""
    try:
        ProductService.delete_product(product_id)
        return success("Product deactivated")
    except ValueError as e:
        return error(str(e), 404)
    except Exception as e:
        return error(str(e), 500)
