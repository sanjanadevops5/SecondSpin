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
def users(app):
    buyer_id = str(ObjectId())
    seller_id = str(ObjectId())
    other_id = str(ObjectId())
    import backend.db
    db = backend.db.get_db()
    
    for uid in [buyer_id, seller_id, other_id]:
        db.users.insert_one({
            '_id': ObjectId(uid),
            'account_status': 'ACTIVE',
            'role': 'student'
        })
        
    return {
        'buyer': ({"Authorization": f"Bearer {generate_token(app, buyer_id)}"}, buyer_id),
        'seller': ({"Authorization": f"Bearer {generate_token(app, seller_id)}"}, seller_id),
        'other': ({"Authorization": f"Bearer {generate_token(app, other_id)}"}, other_id)
    }

@pytest.fixture
def product(app, users):
    import backend.db
    product_id = str(ObjectId())
    seller_id = users['seller'][1]
    backend.db.get_db().products.insert_one({
        '_id': ObjectId(product_id),
        'seller_id': seller_id,
        'category_id': 'textbooks',
        'title': 'Test Product',
        'price': 10,
        'condition': 'NEW',
        'status': 'ACTIVE',
        'created_at': datetime.datetime.now(datetime.timezone.utc)
    })
    return product_id

def test_create_request(client, users, product):
    buyer_headers, buyer_id = users['buyer']
    res = client.post('/api/v1/purchase-requests/', headers=buyer_headers, json={'product_id': product, 'message': 'Hello'})
    assert res.status_code == 201
    assert 'request_id' in res.get_json()['data']

def test_duplicate_pending_request(client, users, product):
    buyer_headers, buyer_id = users['buyer']
    client.post('/api/v1/purchase-requests/', headers=buyer_headers, json={'product_id': product})
    # Try again
    res = client.post('/api/v1/purchase-requests/', headers=buyer_headers, json={'product_id': product})
    assert res.status_code == 409

def test_self_purchase(client, users, product):
    seller_headers, seller_id = users['seller']
    res = client.post('/api/v1/purchase-requests/', headers=seller_headers, json={'product_id': product})
    assert res.status_code == 403

def test_sold_product_request(client, users, app):
    buyer_headers, buyer_id = users['buyer']
    import backend.db
    product_id = str(ObjectId())
    backend.db.get_db().products.insert_one({
        '_id': ObjectId(product_id),
        'seller_id': str(ObjectId()),
        'status': 'SOLD'
    })
    res = client.post('/api/v1/purchase-requests/', headers=buyer_headers, json={'product_id': product_id})
    assert res.status_code == 400

def test_buyer_requests_list(client, users, product):
    buyer_headers, buyer_id = users['buyer']
    client.post('/api/v1/purchase-requests/', headers=buyer_headers, json={'product_id': product})
    
    res = client.get('/api/v1/purchase-requests/mine', headers=buyer_headers)
    assert res.status_code == 200
    items = res.get_json()['data']['items']
    assert len(items) == 1
    assert items[0]['product_id'] == product

def test_seller_received_requests(client, users, product):
    buyer_headers, buyer_id = users['buyer']
    seller_headers, seller_id = users['seller']
    client.post('/api/v1/purchase-requests/', headers=buyer_headers, json={'product_id': product})
    
    res = client.get('/api/v1/purchase-requests/received', headers=seller_headers)
    assert res.status_code == 200
    assert len(res.get_json()['data']['items']) == 1

def test_seller_accept(client, users, product):
    buyer_headers, buyer_id = users['buyer']
    seller_headers, seller_id = users['seller']
    
    # Create request
    res = client.post('/api/v1/purchase-requests/', headers=buyer_headers, json={'product_id': product})
    req_id = res.get_json()['data']['request_id']
    
    # Accept request
    res = client.patch(f'/api/v1/purchase-requests/{req_id}/accept', headers=seller_headers)
    assert res.status_code == 200
    
    # Verify product remains ACTIVE (Phase 6 rule)
    import backend.db
    prod = backend.db.get_db().products.find_one({'_id': ObjectId(product)})
    assert prod['status'] == 'ACTIVE'

def test_buyer_cannot_accept(client, users, product):
    buyer_headers, buyer_id = users['buyer']
    res = client.post('/api/v1/purchase-requests/', headers=buyer_headers, json={'product_id': product})
    req_id = res.get_json()['data']['request_id']
    
    res = client.patch(f'/api/v1/purchase-requests/{req_id}/accept', headers=buyer_headers)
    assert res.status_code == 403

def test_seller_reject(client, users, product):
    buyer_headers, buyer_id = users['buyer']
    seller_headers, seller_id = users['seller']
    
    res = client.post('/api/v1/purchase-requests/', headers=buyer_headers, json={'product_id': product})
    req_id = res.get_json()['data']['request_id']
    
    res = client.patch(f'/api/v1/purchase-requests/{req_id}/reject', headers=seller_headers)
    assert res.status_code == 200
    
    # Verify status is REJECTED
    import backend.db
    req = backend.db.get_db().purchase_requests.find_one({'_id': ObjectId(req_id)})
    assert req['status'] == 'REJECTED'

def test_buyer_cancel(client, users, product):
    buyer_headers, buyer_id = users['buyer']
    
    res = client.post('/api/v1/purchase-requests/', headers=buyer_headers, json={'product_id': product})
    req_id = res.get_json()['data']['request_id']
    
    res = client.patch(f'/api/v1/purchase-requests/{req_id}/cancel', headers=buyer_headers)
    assert res.status_code == 200
    
    import backend.db
    req = backend.db.get_db().purchase_requests.find_one({'_id': ObjectId(req_id)})
    assert req['status'] == 'CANCELLED'

def test_invalid_transition(client, users, product):
    buyer_headers, buyer_id = users['buyer']
    seller_headers, seller_id = users['seller']
    
    res = client.post('/api/v1/purchase-requests/', headers=buyer_headers, json={'product_id': product})
    req_id = res.get_json()['data']['request_id']
    
    # Seller rejects
    client.patch(f'/api/v1/purchase-requests/{req_id}/reject', headers=seller_headers)
    
    # Try to accept a rejected request
    res = client.patch(f'/api/v1/purchase-requests/{req_id}/accept', headers=seller_headers)
    assert res.status_code == 400

def test_unrelated_user_access(client, users, product):
    buyer_headers, buyer_id = users['buyer']
    other_headers, other_id = users['other']
    
    res = client.post('/api/v1/purchase-requests/', headers=buyer_headers, json={'product_id': product})
    req_id = res.get_json()['data']['request_id']
    
    res = client.get(f'/api/v1/purchase-requests/{req_id}', headers=other_headers)
    assert res.status_code == 403

def test_new_request_after_rejection(client, users, product):
    """A buyer whose previous request was REJECTED can submit a fresh request for the same product."""
    buyer_headers, buyer_id = users['buyer']
    seller_headers, seller_id = users['seller']

    # Step 1: Buyer creates initial request
    res = client.post('/api/v1/purchase-requests/', headers=buyer_headers, json={'product_id': product})
    assert res.status_code == 201
    first_req_id = res.get_json()['data']['request_id']

    # Step 2: Seller rejects
    res = client.patch(f'/api/v1/purchase-requests/{first_req_id}/reject', headers=seller_headers)
    assert res.status_code == 200

    # Step 3: Verify first request is REJECTED
    import backend.db
    first_req = backend.db.get_db().purchase_requests.find_one({'_id': __import__('bson').ObjectId(first_req_id)})
    assert first_req['status'] == 'REJECTED'

    # Step 4: Buyer submits a new request for the same product — must succeed
    res = client.post('/api/v1/purchase-requests/', headers=buyer_headers, json={'product_id': product})
    assert res.status_code == 201, f"Expected 201 but got {res.status_code}: {res.get_json()}"
    second_req_id = res.get_json()['data']['request_id']
    assert second_req_id != first_req_id

    # Step 5: Verify new request is PENDING
    second_req = backend.db.get_db().purchase_requests.find_one({'_id': __import__('bson').ObjectId(second_req_id)})
    assert second_req['status'] == 'PENDING'

    # Step 6: Verify old request still REJECTED
    first_req = backend.db.get_db().purchase_requests.find_one({'_id': __import__('bson').ObjectId(first_req_id)})
    assert first_req['status'] == 'REJECTED'

def test_new_request_after_cancellation(client, users, product):
    """A buyer who CANCELLED their previous request can submit a fresh request for the same product."""
    buyer_headers, buyer_id = users['buyer']

    # Step 1: Buyer creates initial request
    res = client.post('/api/v1/purchase-requests/', headers=buyer_headers, json={'product_id': product})
    assert res.status_code == 201
    first_req_id = res.get_json()['data']['request_id']

    # Step 2: Buyer cancels
    res = client.patch(f'/api/v1/purchase-requests/{first_req_id}/cancel', headers=buyer_headers)
    assert res.status_code == 200

    # Step 3: Verify first request is CANCELLED
    import backend.db
    first_req = backend.db.get_db().purchase_requests.find_one({'_id': __import__('bson').ObjectId(first_req_id)})
    assert first_req['status'] == 'CANCELLED'

    # Step 4: Buyer submits a new request for the same product — must succeed
    res = client.post('/api/v1/purchase-requests/', headers=buyer_headers, json={'product_id': product})
    assert res.status_code == 201, f"Expected 201 but got {res.status_code}: {res.get_json()}"
    second_req_id = res.get_json()['data']['request_id']
    assert second_req_id != first_req_id

    # Step 5: Verify new request is PENDING
    second_req = backend.db.get_db().purchase_requests.find_one({'_id': __import__('bson').ObjectId(second_req_id)})
    assert second_req['status'] == 'PENDING'

    # Step 6: Verify old request still CANCELLED
    first_req = backend.db.get_db().purchase_requests.find_one({'_id': __import__('bson').ObjectId(first_req_id)})
    assert first_req['status'] == 'CANCELLED'

