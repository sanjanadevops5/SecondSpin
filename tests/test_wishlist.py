import pytest
from bson.objectid import ObjectId
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
def setup_product(app):
    import backend.db
    product_id = str(ObjectId())
    backend.db.get_db().products.insert_one({
        '_id': ObjectId(product_id),
        'seller_id': str(ObjectId()),
        'category_id': 'textbooks',
        'title': 'Test Product',
        'price': 10,
        'condition': 'NEW',
        'status': 'ACTIVE',
        'created_at': datetime.datetime.now(datetime.timezone.utc)
    })
    return product_id

def test_add_to_wishlist(client, auth_headers, setup_product):
    headers, user_id = auth_headers
    product_id = setup_product
    
    res = client.post('/api/v1/wishlist/', headers=headers, json={'product_id': product_id})
    assert res.status_code == 201
    assert 'wishlist_id' in res.get_json()['data']

def test_add_to_wishlist_duplicate(client, auth_headers, setup_product):
    headers, user_id = auth_headers
    product_id = setup_product
    
    res1 = client.post('/api/v1/wishlist/', headers=headers, json={'product_id': product_id})
    assert res1.status_code == 201
    
    res2 = client.post('/api/v1/wishlist/', headers=headers, json={'product_id': product_id})
    assert res2.status_code == 409

def test_add_to_wishlist_sold_product(client, auth_headers, app):
    headers, user_id = auth_headers
    import backend.db
    product_id = str(ObjectId())
    backend.db.get_db().products.insert_one({
        '_id': ObjectId(product_id),
        'seller_id': str(ObjectId()),
        'status': 'SOLD'
    })
    
    res = client.post('/api/v1/wishlist/', headers=headers, json={'product_id': product_id})
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'UNAVAILABLE'

def test_get_wishlist(client, auth_headers, setup_product):
    headers, user_id = auth_headers
    product_id = setup_product
    
    client.post('/api/v1/wishlist/', headers=headers, json={'product_id': product_id})
    
    res = client.get('/api/v1/wishlist/', headers=headers)
    assert res.status_code == 200
    items = res.get_json()['data']['items']
    assert len(items) == 1
    assert items[0]['product']['id'] == product_id

def test_get_wishlist_cross_user(client, auth_headers, other_auth_headers, setup_product):
    headers, user_id = auth_headers
    other_headers, other_id = other_auth_headers
    product_id = setup_product
    
    client.post('/api/v1/wishlist/', headers=headers, json={'product_id': product_id})
    
    # Other user should have empty wishlist
    res = client.get('/api/v1/wishlist/', headers=other_headers)
    assert res.status_code == 200
    items = res.get_json()['data']['items']
    assert len(items) == 0

def test_remove_from_wishlist(client, auth_headers, setup_product):
    headers, user_id = auth_headers
    product_id = setup_product
    
    client.post('/api/v1/wishlist/', headers=headers, json={'product_id': product_id})
    
    res = client.delete(f'/api/v1/wishlist/{product_id}', headers=headers)
    assert res.status_code == 200
    
    res2 = client.get('/api/v1/wishlist/', headers=headers)
    assert len(res2.get_json()['data']['items']) == 0

def test_remove_nonexistent(client, auth_headers):
    headers, user_id = auth_headers
    res = client.delete(f'/api/v1/wishlist/{str(ObjectId())}', headers=headers)
    assert res.status_code == 404
