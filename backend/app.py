import logging
from flask import Flask
from flask_cors import CORS
from .config import Config
from .routes import api_v1_bp
from .routes.categories import categories_bp
from .routes.products import products_bp
from .routes.wishlist import wishlist_bp
from .routes.purchase_requests import purchase_requests_bp
from .routes.transactions import transactions_bp
from .routes.reviews import reviews_bp
from .errors import register_error_handlers


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure CORS securely from environment
    cors_origins = app.config.get('CORS_ORIGINS', '*')
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})

    # Configure logging
    logging.basicConfig(
        level=logging.INFO if app.config['FLASK_ENV'] != 'development' else logging.DEBUG,
        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
    )
    # Ensure secrets/tokens aren't logged easily
    app.logger.info("Application starting up...")

    # Initialize extensions
    from .db import init_app
    init_app(app)

    # Register blueprints
    app.register_blueprint(api_v1_bp)
    app.register_blueprint(categories_bp, url_prefix='/api/v1/categories')
    app.register_blueprint(products_bp, url_prefix='/api/v1/products')
    app.register_blueprint(wishlist_bp, url_prefix='/api/v1/wishlist')
    app.register_blueprint(purchase_requests_bp, url_prefix='/api/v1/purchase-requests')
    app.register_blueprint(transactions_bp, url_prefix='/api/v1/transactions')
    app.register_blueprint(reviews_bp, url_prefix='/api/v1/reviews')

    # Register error handlers
    register_error_handlers(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=(app.config['FLASK_ENV'] == 'development'))
