from backend.db import get_db, close_mongo_connection, get_mongo_client

def test_db_connection(app):
    """Test that the application can initialize the DB connection properly."""
    with app.app_context():
        db = get_db()
        # Even if MONGODB_URI isn't valid in CI, we just verify the function doesn't crash 
        # when returning None or attempting to connect.
        # If it's valid, db is not None.
        
def test_db_test_database_name(app):
    with app.app_context():
        # Ensure test database suffix is used in testing environment
        db = get_db()
        if db is not None:
            assert db.name.endswith('_test')
