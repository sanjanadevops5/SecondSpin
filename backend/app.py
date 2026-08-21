import logging
from flask import Flask
from flask_cors import CORS
from .config import Config
from .routes import api_bp
from .errors import register_error_handlers


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure CORS
    CORS(app)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO if app.config['FLASK_ENV'] != 'development' else logging.DEBUG,
        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
    )
    # Ensure secrets/tokens aren't logged easily
    app.logger.info("Application starting up...")

    # Initialize extensions (Database etc. will go here later)
    # e.g., init_db(app)

    # Register blueprints
    app.register_blueprint(api_bp)

    # Register error handlers
    register_error_handlers(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=(app.config['FLASK_ENV'] == 'development'))
