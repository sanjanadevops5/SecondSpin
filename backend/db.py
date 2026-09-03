import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from flask import current_app, g

logger = logging.getLogger(__name__)

# Global client instance to reuse connection across requests
_mongo_client = None

def get_mongo_client(app=None):
    """
    Returns a reusable MongoDB client instance.
    Initializes it if it hasn't been created yet.
    """
    global _mongo_client
    
    if app is None:
        app = current_app
        
    if _mongo_client is None:
        mongo_uri = app.config.get('MONGODB_URI')
        
        if not mongo_uri or mongo_uri == 'mongomock':
            logger.info("MONGODB_URI is not set or set to mongomock. Using in-memory mongomock database.")
            import mongomock
            _mongo_client = mongomock.MongoClient()
            return _mongo_client

        try:
            logger.info("Initializing MongoDB client...")
            _mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            _mongo_client.admin.command('ping')
            logger.info("Successfully connected to MongoDB.")
        except (ConnectionFailure, ConfigurationError) as e:
            logger.warning(f"Failed to connect to real MongoDB ({e}). Falling back to in-memory mongomock database.")
            import mongomock
            _mongo_client = mongomock.MongoClient()
            
    return _mongo_client

def get_db(app=None):
    """
    Gets the current database instance for the application.
    Uses the MONGODB_DATABASE config variable.
    """
    if app is None:
        app = current_app
        
    client = get_mongo_client(app)
    if client is None:
        return None
        
    db_name = app.config.get('MONGODB_DATABASE', 'secondspin')
    
    # Check if we're in testing mode, and if so, suffix the database name
    # if it doesn't already have one, to avoid polluting dev/prod DBs.
    if app.config.get('TESTING'):
        if not db_name.endswith('_test'):
            db_name = f"{db_name}_test"
            
    return client[db_name]

def close_mongo_connection():
    """Close the global MongoDB client connection."""
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
        logger.info("MongoDB connection closed.")

def init_app(app):
    """Register database teardown with Flask app."""
    # Note: get_mongo_client(app) is typically called lazily when first needed,
    # but we could call it here to eagerly connect on startup if desired.
    # For robust server startup even without DB, we'll keep it lazy.
    
    @app.teardown_appcontext
    def teardown_db(exception):
        # We don't close the global client per-request (PyMongo manages its own connection pool).
        # We just clean up any request-local DB objects if we used them (like 'g.db').
        db = g.pop('db', None)
