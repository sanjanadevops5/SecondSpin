import pytest
from backend.app import create_app
from backend.config import Config


class TestConfig(Config):
    TESTING = True
    FLASK_ENV = 'testing'


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(TestConfig)
    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
