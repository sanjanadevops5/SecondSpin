import pytest
from backend.app import create_app
from backend.config import Config
import mongomock

class TestConfig(Config):
    TESTING = True
    FLASK_ENV = 'testing'
    JWT_SECRET_KEY = 'test-secret-key-must-be-32-bytes-long'


@pytest.fixture
def app(monkeypatch):
    """Create and configure a new app instance for each test."""
    # Mock MongoDB
    mock_db = mongomock.MongoClient().db
    monkeypatch.setattr("backend.models.user.get_db", lambda *args, **kwargs: mock_db)
    monkeypatch.setattr("backend.db.get_db", lambda *args, **kwargs: mock_db)

    app = create_app(TestConfig)
    
    # Setup indexes for mock_db
    with app.app_context():
        from backend.models.product import ProductModel
        from backend.models.wishlist import WishlistModel
        from backend.models.purchase_request import PurchaseRequestModel
        from backend.models.transaction import TransactionModel
        from backend.models.review import ReviewModel
        
        ProductModel.setup_indexes()
        WishlistModel.setup_indexes()
        PurchaseRequestModel.setup_indexes()
        TransactionModel.setup_indexes()
        ReviewModel.setup_indexes()

    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
