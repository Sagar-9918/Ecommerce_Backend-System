"""
app.py
──────
E-Commerce Backend — Flask Application Entry Point
Amazon-like Architecture | Layered Design | JWT Auth | MySQL

Run:
    python app.py

Or with environment variables:
    DB_PASSWORD=secret python app.py
"""

from flask import Flask, jsonify
from config import config

# ── Route blueprints ───────────────────────────────────────────
from routes.auth_routes    import auth_bp
from routes.product_routes import products_bp
from routes.cart_routes    import cart_bp
from routes.order_routes   import orders_bp


def create_app() -> Flask:
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)

    # ── App config ─────────────────────────────────────────────
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["DEBUG"]      = config.DEBUG

    # ── Register blueprints ────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)

    # ── Root health check ──────────────────────────────────────
    @app.route("/")
    def index():
        return jsonify({
            "success": True,
            "message": "🛒 E-Commerce API is running",
            "version": "1.0.0",
            "endpoints": {
                "auth":     "/auth",
                "products": "/products",
                "cart":     "/cart",
                "orders":   "/orders"
            }
        })

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy", "service": "ecommerce-api"})

    # ── Global error handlers ──────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "message": "Endpoint not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "message": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"success": False, "message": "Internal server error"}), 500

    return app


# ── Entry point ────────────────────────────────────────────────
if __name__ == "__main__":
    app = create_app()
    print("=" * 55)
    print("  🛒  E-Commerce Backend API")
    print("=" * 55)
    print(f"  Server  : http://localhost:5000")
    print(f"  Debug   : {config.DEBUG}")
    print(f"  Database: {config.DB_NAME} @ {config.DB_HOST}")
    print("=" * 55)
    app.run(host="0.0.0.0", port=5000, debug=config.DEBUG)
