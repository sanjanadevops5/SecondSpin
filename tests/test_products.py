import pytest
from bson.objectid import ObjectId
import json
import jwt
import datetime

def generate_token(app, user_id, role="student"):
    secret = app.config.get('JWT_SECRET_KEY')
    expires_in = app.config.get('JWT_EXPIRES_IN', 86400)
    token = jwt.encode({
        'sub': user_id,
        'role': role,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expires_in),
        'iat': datetime.datetime.now(datetime.timezone.utc)
    }, secret, algorithm="HS256")
    return token

@pytest.fixture
def auth_headers(app):
    user_id = str(ObjectId())
    # Mock user creation so jwt middleware finds the user
    import backend.db
    backend.db.get_db().users.insert_one({
        '_id': ObjectId(user_id),
        'account_status': 'ACTIVE',
        'role': 'student'
    })
    token = generate_token(app, user_id)
    return {"Authorization": f"Bearer {token}"}, user_id

@pytest.fixture
def other_auth_headers(app):
    user_id = str(ObjectId())
    import backend.db
    backend.db.get_db().users.insert_one({
        '_id': ObjectId(user_id),
        'account_status': 'ACTIVE',
        'role': 'student'
    })
    token = generate_token(app, user_id)
    return {"Authorization": f"Bearer {token}"}, user_id

@pytest.fixture
def setup_categories(app):
    import backend.db
    backend.db.get_db().categories.insert_one({'slug': 'textbooks', 'is_active': True})

def test_create_product_success(client, auth_headers, setup_categories):
    headers, user_id = auth_headers
    payload = {
        "title": "Calculus Book",
        "description": "Like new.",
        "price": 20.50,
        "category_id": "textbooks",
        "condition": "GOOD"
    }
    res = client.post('/api/v1/products/', headers=headers, json=payload)
    assert res.status_code == 201
    assert res.get_json()['success'] is True
    assert 'product_id' in res.get_json()['data']

def test_create_product_unauthenticated(client, setup_categories):
    payload = {
        "title": "Calculus Book",
        "description": "Like new.",
        "price": 20.50,
        "category_id": "textbooks",
        "condition": "GOOD"
    }
    res = client.post('/api/v1/products/', json=payload)
    assert res.status_code == 401

def test_create_product_invalid_category(client, auth_headers):
    headers, user_id = auth_headers
    payload = {
        "title": "Calculus Book",
        "description": "Like new.",
        "price": 20.50,
        "category_id": "invalid-cat",
        "condition": "GOOD"
    }
    res = client.post('/api/v1/products/', headers=headers, json=payload)
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'INVALID_CATEGORY'

def test_create_product_invalid_price(client, auth_headers, setup_categories):
    headers, user_id = auth_headers
    payload = {
        "title": "Calculus Book",
        "description": "Like new.",
        "price": -5,
        "category_id": "textbooks",
        "condition": "GOOD"
    }
    res = client.post('/api/v1/products/', headers=headers, json=payload)
    assert res.status_code == 400

def test_get_product(client, auth_headers, setup_categories):
    headers, user_id = auth_headers
    payload = {
        "title": "Test Book",
        "description": "Test.",
        "price": 10,
        "category_id": "textbooks",
        "condition": "NEW"
    }
    res = client.post('/api/v1/products/', headers=headers, json=payload)
    product_id = res.get_json()['data']['product_id']

    res = client.get(f'/api/v1/products/{product_id}')
    assert res.status_code == 200
    data = res.get_json()['data']
    assert data['title'] == "Test Book"
    assert data['seller']['id'] == user_id
    assert 'password_hash' not in data['seller']

def test_update_product_owner(client, auth_headers, setup_categories):
    headers, user_id = auth_headers
    payload = {
        "title": "Original",
        "description": "Test.",
        "price": 10,
        "category_id": "textbooks",
        "condition": "NEW"
    }
    res = client.post('/api/v1/products/', headers=headers, json=payload)
    product_id = res.get_json()['data']['product_id']

    res = client.put(f'/api/v1/products/{product_id}', headers=headers, json={"title": "Updated"})
    assert res.status_code == 200

    res2 = client.get(f'/api/v1/products/{product_id}')
    assert res2.get_json()['data']['title'] == "Updated"

def test_update_product_non_owner(client, auth_headers, other_auth_headers, setup_categories):
    headers, user_id = auth_headers
    other_headers, other_id = other_auth_headers

    payload = {
        "title": "Original",
        "description": "Test.",
        "price": 10,
        "category_id": "textbooks",
        "condition": "NEW"
    }
    res = client.post('/api/v1/products/', headers=headers, json=payload)
    product_id = res.get_json()['data']['product_id']

    res = client.put(f'/api/v1/products/{product_id}', headers=other_headers, json={"title": "Hacked"})
    assert res.status_code == 403

def test_delete_product_owner(client, auth_headers, setup_categories):
    headers, user_id = auth_headers
    payload = {
        "title": "To Delete",
        "description": "Test.",
        "price": 10,
        "category_id": "textbooks",
        "condition": "NEW"
    }
    res = client.post('/api/v1/products/', headers=headers, json=payload)
    product_id = res.get_json()['data']['product_id']

    res = client.delete(f'/api/v1/products/{product_id}', headers=headers)
    assert res.status_code == 200

    # Verify it is REMOVED
    res2 = client.get(f'/api/v1/products/{product_id}')
    assert res2.status_code == 404
    assert "removed" in res2.get_json()['error']['message'].lower()

def test_delete_product_non_owner(client, auth_headers, other_auth_headers, setup_categories):
    headers, user_id = auth_headers
    other_headers, other_id = other_auth_headers

    payload = {
        "title": "Keep Me",
        "description": "Test.",
        "price": 10,
        "category_id": "textbooks",
        "condition": "NEW"
    }
    res = client.post('/api/v1/products/', headers=headers, json=payload)
    product_id = res.get_json()['data']['product_id']

    res = client.delete(f'/api/v1/products/{product_id}', headers=other_headers)
    assert res.status_code == 403

def test_discovery_pagination_filtering(client, auth_headers, setup_categories):
    headers, user_id = auth_headers
    # Seed 25 products
    for i in range(25):
        client.post('/api/v1/products/', headers=headers, json={
            "title": f"Book {i}",
            "description": "Test.",
            "price": 10 + i,
            "category_id": "textbooks",
            "condition": "NEW" if i % 2 == 0 else "GOOD"
        })

    # Default pagination
    res = client.get('/api/v1/products/')
    assert res.status_code == 200
    data = res.get_json()['data']
    assert len(data['items']) == 20
    assert data['pagination']['total'] == 25
    assert data['pagination']['pages'] == 2
    
    # Page 2
    res = client.get('/api/v1/products/?page=2')
    data = res.get_json()['data']
    assert len(data['items']) == 5

    # Filter Condition
    res = client.get('/api/v1/products/?condition=NEW')
    data = res.get_json()['data']
    assert data['pagination']['total'] == 13 # 25 products, 0 to 24, evens are 13

    # Filter Price
    res = client.get('/api/v1/products/?min_price=20&max_price=30')
    data = res.get_json()['data']
    # Prices are 10 to 34. min 20 max 30 means i=10 to i=20 (11 items)
    assert data['pagination']['total'] == 11
