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
    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
