"""
Comprehensive Phase 7 Transaction Tests

Covers:
  - Valid transaction creation (buyer only, from ACCEPTED PR)
  - All error cases (unauthenticated, invalid PR, non-ACCEPTED PR, product states, self-purchase, duplicates)
  - Product reservation on creation
  - Reserve lifecycle (PENDING → RESERVED)
  - Complete lifecycle (RESERVED → COMPLETED, product → SOLD)
  - Cancel lifecycle (PENDING/RESERVED → CANCELLED, product → ACTIVE)
  - Invalid status transitions
  - Authorization (buyer, seller, unrelated user)
  - History endpoints (mine, received)
  - Detail endpoint with ownership enforcement
  - Client-side field manipulation (buyer_id, seller_id, status injection)
"""
import pytest
import datetime
import jwt
from bson.objectid import ObjectId
import backend.db


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def generate_token(app, user_id, role='student'):
    secret     = app.config.get('JWT_SECRET_KEY')
    expires_in = app.config.get('JWT_EXPIRES_IN', 86400)
    return jwt.encode(
        {
            'sub': user_id,
            'role': role,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expires_in),
            'iat': datetime.datetime.now(datetime.timezone.utc),
        },
        secret,
        algorithm='HS256',
    )


def make_headers(app, user_id):
    return {'Authorization': f'Bearer {generate_token(app, user_id)}'}


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def users(app):
    """Creates buyer, seller, and unrelated (other) users in the mock DB."""
    db = backend.db.get_db()
    buyer_id  = str(ObjectId())
    seller_id = str(ObjectId())
    other_id  = str(ObjectId())
    for uid in [buyer_id, seller_id, other_id]:
        db.users.insert_one({'_id': ObjectId(uid), 'account_status': 'ACTIVE', 'role': 'student'})
    return {
        'buyer':  (make_headers(app, buyer_id),  buyer_id),
        'seller': (make_headers(app, seller_id), seller_id),
        'other':  (make_headers(app, other_id),  other_id),
    }


@pytest.fixture
def product(app, users):
    """Creates an ACTIVE product owned by the seller."""
    db        = backend.db.get_db()
    product_id = str(ObjectId())
    seller_id  = users['seller'][1]
    db.products.insert_one({
        '_id':        ObjectId(product_id),
        'seller_id':  seller_id,
        'category_id': 'textbooks',
        'title':      'Test Product',
        'price':      100.0,
        'condition':  'GOOD',
        'status':     'ACTIVE',
        'created_at': datetime.datetime.now(datetime.timezone.utc),
        'updated_at': datetime.datetime.now(datetime.timezone.utc),
    })
    return product_id


@pytest.fixture
def accepted_pr(app, users, product):
    """Creates an ACCEPTED purchase request from buyer → seller for the test product."""
    db        = backend.db.get_db()
    pr_id     = str(ObjectId())
    buyer_id  = users['buyer'][1]
    seller_id = users['seller'][1]
    db.purchase_requests.insert_one({
        '_id':        ObjectId(pr_id),
        'product_id': product,
        'buyer_id':   buyer_id,
        'seller_id':  seller_id,
        'message':    'I want to buy this.',
        'status':     'ACCEPTED',
        'created_at': datetime.datetime.now(datetime.timezone.utc),
        'updated_at': datetime.datetime.now(datetime.timezone.utc),
        'responded_at': datetime.datetime.now(datetime.timezone.utc),
    })
    return pr_id


@pytest.fixture
def pending_pr(app, users, product):
    """Creates a PENDING purchase request."""
    db        = backend.db.get_db()
    pr_id     = str(ObjectId())
    buyer_id  = users['buyer'][1]
    seller_id = users['seller'][1]
    db.purchase_requests.insert_one({
        '_id':        ObjectId(pr_id),
        'product_id': product,
        'buyer_id':   buyer_id,
        'seller_id':  seller_id,
        'message':    '',
        'status':     'PENDING',
        'created_at': datetime.datetime.now(datetime.timezone.utc),
        'updated_at': datetime.datetime.now(datetime.timezone.utc),
        'responded_at': None,
    })
    return pr_id


@pytest.fixture
def transaction(app, users, accepted_pr, product):
    """
    Creates a PENDING transaction (via API) and returns its ID.
    Product will be RESERVED after this fixture runs.
    """
    buyer_headers = users['buyer'][0]
    client_obj    = app.test_client()
    res = client_obj.post(
        '/api/v1/transactions/',
        headers=buyer_headers,
        json={'purchase_request_id': accepted_pr},
    )
    assert res.status_code == 201, f'Transaction fixture failed: {res.get_json()}'
    return res.get_json()['data']['transaction_id']


@pytest.fixture
def reserved_transaction(app, users, transaction):
    """Advances the transaction to RESERVED status."""
    seller_headers = users['seller'][0]
    client_obj     = app.test_client()
    res = client_obj.patch(
        f'/api/v1/transactions/{transaction}/reserve',
        headers=seller_headers,
    )
    assert res.status_code == 200, f'Reserve fixture failed: {res.get_json()}'
    return transaction


@pytest.fixture
def completed_transaction(app, users, reserved_transaction):
    """Advances the transaction to COMPLETED status (product becomes SOLD)."""
    seller_headers = users['seller'][0]
    client_obj     = app.test_client()
    res = client_obj.patch(
        f'/api/v1/transactions/{reserved_transaction}/complete',
        headers=seller_headers,
    )
    assert res.status_code == 200, f'Complete fixture failed: {res.get_json()}'
    return reserved_transaction


# ─────────────────────────────────────────────────────────────────────────────
# Transaction Creation
# ─────────────────────────────────────────────────────────────────────────────

def test_create_transaction_valid(client, users, accepted_pr):
    """Happy path: buyer creates a transaction from an ACCEPTED purchase request."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/transactions/', headers=buyer_headers,
                      json={'purchase_request_id': accepted_pr})
    assert res.status_code == 201
    assert 'transaction_id' in res.get_json()['data']


def test_create_transaction_unauthenticated(client, accepted_pr):
    """Unauthenticated request is rejected with 401."""
    res = client.post('/api/v1/transactions/', json={'purchase_request_id': accepted_pr})
    assert res.status_code == 401


def test_create_transaction_missing_field(client, users):
    """Missing purchase_request_id returns 422."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/transactions/', headers=buyer_headers, json={})
    assert res.status_code == 422


def test_create_transaction_invalid_pr_id(client, users):
    """Non-existent purchase_request_id returns 404."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/transactions/', headers=buyer_headers,
                      json={'purchase_request_id': str(ObjectId())})
    assert res.status_code == 404


def test_create_transaction_pr_not_accepted_pending(client, users, pending_pr):
    """A PENDING PR cannot be used to create a transaction."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/transactions/', headers=buyer_headers,
                      json={'purchase_request_id': pending_pr})
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'INVALID_STATE'


def test_create_transaction_pr_not_accepted_rejected(client, users, product):
    """A REJECTED PR cannot be used to create a transaction."""
    db = backend.db.get_db()
    pr_id = str(ObjectId())
    buyer_id, seller_id = users['buyer'][1], users['seller'][1]
    db.purchase_requests.insert_one({
        '_id': ObjectId(pr_id), 'product_id': product,
        'buyer_id': buyer_id, 'seller_id': seller_id,
        'status': 'REJECTED', 'created_at': datetime.datetime.now(datetime.timezone.utc),
        'updated_at': datetime.datetime.now(datetime.timezone.utc), 'responded_at': None, 'message': '',
    })
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/transactions/', headers=buyer_headers,
                      json={'purchase_request_id': pr_id})
    assert res.status_code == 400


def test_create_transaction_not_buyer(client, users, accepted_pr):
    """Seller cannot create a transaction on a PR where they are the seller."""
    seller_headers, _ = users['seller']
    res = client.post('/api/v1/transactions/', headers=seller_headers,
                      json={'purchase_request_id': accepted_pr})
    assert res.status_code == 403


def test_create_transaction_unrelated_user(client, users, accepted_pr):
    """An unrelated user cannot create a transaction."""
    other_headers, _ = users['other']
    res = client.post('/api/v1/transactions/', headers=other_headers,
                      json={'purchase_request_id': accepted_pr})
    assert res.status_code == 403


def test_create_transaction_product_sold(client, users, accepted_pr, product):
    """Cannot create a transaction if the product is already SOLD."""
    db = backend.db.get_db()
    db.products.update_one({'_id': ObjectId(product)}, {'$set': {'status': 'SOLD'}})
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/transactions/', headers=buyer_headers,
                      json={'purchase_request_id': accepted_pr})
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'UNAVAILABLE'


def test_create_transaction_product_removed(client, users, accepted_pr, product):
    """Cannot create a transaction if the product is REMOVED."""
    db = backend.db.get_db()
    db.products.update_one({'_id': ObjectId(product)}, {'$set': {'status': 'REMOVED'}})
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/transactions/', headers=buyer_headers,
                      json={'purchase_request_id': accepted_pr})
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'UNAVAILABLE'


def test_create_transaction_product_already_reserved(client, users, accepted_pr, product):
    """Cannot create a transaction if the product already has an active transaction."""
    db = backend.db.get_db()
    # Simulate existing active transaction
    db.transactions.insert_one({
        '_id': ObjectId(), 'purchase_request_id': str(ObjectId()),
        'product_id': product, 'buyer_id': str(ObjectId()), 'seller_id': users['seller'][1],
        'status': 'PENDING',
        'created_at': datetime.datetime.now(datetime.timezone.utc),
        'updated_at': datetime.datetime.now(datetime.timezone.utc),
        'completed_at': None, 'cancelled_at': None,
    })
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/transactions/', headers=buyer_headers,
                      json={'purchase_request_id': accepted_pr})
    assert res.status_code == 409


def test_create_transaction_duplicate(client, users, accepted_pr, transaction):
    """
    Cannot create a second transaction for the same purchase request.
    The product-level active-transaction guard fires first (CONFLICT),
    because the first transaction left the product in PENDING/RESERVED state.
    Either CONFLICT or DUPLICATE_TRANSACTION are acceptable 409 responses.
    """
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/transactions/', headers=buyer_headers,
                      json={'purchase_request_id': accepted_pr})
    assert res.status_code == 409
    code = res.get_json()['error']['code']
    assert code in ('CONFLICT', 'DUPLICATE_TRANSACTION'), f"Unexpected code: {code}"


def test_product_becomes_reserved_on_transaction_creation(client, users, accepted_pr, product):
    """Product status becomes RESERVED after a transaction is created."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/transactions/', headers=buyer_headers,
                      json={'purchase_request_id': accepted_pr})
    assert res.status_code == 201
    db      = backend.db.get_db()
    product_doc = db.products.find_one({'_id': ObjectId(product)})
    assert product_doc['status'] == 'RESERVED'


def test_client_cannot_inject_buyer_id(client, users, accepted_pr):
    """
    Client-supplied buyer_id in the body must be ignored.
    The server always derives buyer_id from the JWT and from the PR.
    """
    other_headers, other_id = users['other']
    # Other user tries to supply the accepted PR which is owned by buyer
    # The server should derive buyer from PR → reject because other != PR buyer
    res = client.post('/api/v1/transactions/', headers=other_headers,
                      json={'purchase_request_id': accepted_pr, 'buyer_id': users['buyer'][1]})
    # Should be 403 since other != PR's buyer_id
    assert res.status_code == 403


def test_client_cannot_inject_seller_id(client, users, accepted_pr):
    """seller_id is always derived from the purchase request, not from the request body."""
    buyer_headers, _ = users['buyer']
    fake_seller_id   = str(ObjectId())
    res = client.post('/api/v1/transactions/', headers=buyer_headers,
                      json={'purchase_request_id': accepted_pr, 'seller_id': fake_seller_id})
    # Should succeed (field ignored) and use real seller from PR
    assert res.status_code == 201
    db = backend.db.get_db()
    txn = db.transactions.find_one({'purchase_request_id': accepted_pr})
    assert txn['seller_id'] != fake_seller_id
    assert txn['seller_id'] == users['seller'][1]


def test_client_cannot_inject_status(client, users, accepted_pr):
    """Client-supplied status in the body must be ignored; transaction always starts PENDING."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/transactions/', headers=buyer_headers,
                      json={'purchase_request_id': accepted_pr, 'status': 'COMPLETED'})
    assert res.status_code == 201
    db  = backend.db.get_db()
    txn = db.transactions.find_one({'purchase_request_id': accepted_pr})
    assert txn['status'] == 'PENDING'


# ─────────────────────────────────────────────────────────────────────────────
# Reserve (PENDING → RESERVED)
# ─────────────────────────────────────────────────────────────────────────────

def test_reserve_transaction_valid(client, users, transaction):
    """Seller can advance PENDING → RESERVED."""
    seller_headers, _ = users['seller']
    res = client.patch(f'/api/v1/transactions/{transaction}/reserve', headers=seller_headers)
    assert res.status_code == 200
    db  = backend.db.get_db()
    txn = db.transactions.find_one({'_id': ObjectId(transaction)})
    assert txn['status'] == 'RESERVED'


def test_reserve_transaction_unauthenticated(client, transaction):
    res = client.patch(f'/api/v1/transactions/{transaction}/reserve')
    assert res.status_code == 401


def test_reserve_transaction_buyer_forbidden(client, users, transaction):
    """Buyer cannot advance a transaction to RESERVED."""
    buyer_headers, _ = users['buyer']
    res = client.patch(f'/api/v1/transactions/{transaction}/reserve', headers=buyer_headers)
    assert res.status_code == 403


def test_reserve_transaction_other_user_forbidden(client, users, transaction):
    """Unrelated user cannot advance a transaction to RESERVED."""
    other_headers, _ = users['other']
    res = client.patch(f'/api/v1/transactions/{transaction}/reserve', headers=other_headers)
    assert res.status_code == 403


def test_reserve_already_reserved(client, users, reserved_transaction):
    """Cannot reserve an already RESERVED transaction."""
    seller_headers, _ = users['seller']
    res = client.patch(f'/api/v1/transactions/{reserved_transaction}/reserve', headers=seller_headers)
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'INVALID_TRANSITION'


def test_reserve_not_found(client, users):
    seller_headers, _ = users['seller']
    res = client.patch(f'/api/v1/transactions/{str(ObjectId())}/reserve', headers=seller_headers)
    assert res.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# Complete (RESERVED → COMPLETED)
# ─────────────────────────────────────────────────────────────────────────────

def test_complete_transaction_valid(client, users, reserved_transaction, product):
    """Seller can complete a RESERVED transaction; product becomes SOLD."""
    seller_headers, _ = users['seller']
    res = client.patch(f'/api/v1/transactions/{reserved_transaction}/complete', headers=seller_headers)
    assert res.status_code == 200
    db  = backend.db.get_db()
    txn = db.transactions.find_one({'_id': ObjectId(reserved_transaction)})
    assert txn['status'] == 'COMPLETED'
    assert txn['completed_at'] is not None


def test_product_sold_on_completion(client, users, reserved_transaction, product):
    """Product transitions to SOLD when a RESERVED transaction is completed."""
    seller_headers, _ = users['seller']
    client.patch(f'/api/v1/transactions/{reserved_transaction}/complete', headers=seller_headers)
    db          = backend.db.get_db()
    product_doc = db.products.find_one({'_id': ObjectId(product)})
    assert product_doc['status'] == 'SOLD'


def test_complete_transaction_unauthenticated(client, reserved_transaction):
    res = client.patch(f'/api/v1/transactions/{reserved_transaction}/complete')
    assert res.status_code == 401


def test_complete_transaction_buyer_forbidden(client, users, reserved_transaction):
    """Buyer cannot complete a transaction."""
    buyer_headers, _ = users['buyer']
    res = client.patch(f'/api/v1/transactions/{reserved_transaction}/complete', headers=buyer_headers)
    assert res.status_code == 403


def test_complete_transaction_other_user_forbidden(client, users, reserved_transaction):
    other_headers, _ = users['other']
    res = client.patch(f'/api/v1/transactions/{reserved_transaction}/complete', headers=other_headers)
    assert res.status_code == 403


def test_complete_from_pending_invalid(client, users, transaction):
    """Cannot complete a PENDING transaction — must go through RESERVED first."""
    seller_headers, _ = users['seller']
    res = client.patch(f'/api/v1/transactions/{transaction}/complete', headers=seller_headers)
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'INVALID_TRANSITION'


def test_complete_already_completed(client, users, completed_transaction):
    """Cannot complete a COMPLETED transaction."""
    seller_headers, _ = users['seller']
    res = client.patch(f'/api/v1/transactions/{completed_transaction}/complete', headers=seller_headers)
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'INVALID_TRANSITION'


def test_complete_not_found(client, users):
    seller_headers, _ = users['seller']
    res = client.patch(f'/api/v1/transactions/{str(ObjectId())}/complete', headers=seller_headers)
    assert res.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# Cancel
# ─────────────────────────────────────────────────────────────────────────────

def test_cancel_pending_by_buyer(client, users, transaction, product):
    """Buyer can cancel a PENDING transaction; product returns to ACTIVE."""
    buyer_headers, _ = users['buyer']
    res = client.patch(f'/api/v1/transactions/{transaction}/cancel', headers=buyer_headers)
    assert res.status_code == 200
    db  = backend.db.get_db()
    txn = db.transactions.find_one({'_id': ObjectId(transaction)})
    assert txn['status'] == 'CANCELLED'
    assert txn['cancelled_at'] is not None


def test_product_returns_to_active_on_cancel(client, users, transaction, product):
    """Product returns to ACTIVE when a PENDING transaction is cancelled."""
    buyer_headers, _ = users['buyer']
    client.patch(f'/api/v1/transactions/{transaction}/cancel', headers=buyer_headers)
    db          = backend.db.get_db()
    product_doc = db.products.find_one({'_id': ObjectId(product)})
    assert product_doc['status'] == 'ACTIVE'


def test_cancel_pending_by_seller(client, users, transaction, product):
    """Seller can also cancel a PENDING transaction."""
    seller_headers, _ = users['seller']
    res = client.patch(f'/api/v1/transactions/{transaction}/cancel', headers=seller_headers)
    assert res.status_code == 200


def test_cancel_reserved_by_buyer(client, users, reserved_transaction, product):
    """Buyer can cancel a RESERVED transaction."""
    buyer_headers, _ = users['buyer']
    res = client.patch(f'/api/v1/transactions/{reserved_transaction}/cancel', headers=buyer_headers)
    assert res.status_code == 200
    db  = backend.db.get_db()
    txn = db.transactions.find_one({'_id': ObjectId(reserved_transaction)})
    assert txn['status'] == 'CANCELLED'


def test_cancel_reserved_by_seller(client, users, reserved_transaction):
    """Seller can cancel a RESERVED transaction."""
    seller_headers, _ = users['seller']
    res = client.patch(f'/api/v1/transactions/{reserved_transaction}/cancel', headers=seller_headers)
    assert res.status_code == 200


def test_cancel_other_user_forbidden(client, users, transaction):
    """Unrelated user cannot cancel a transaction."""
    other_headers, _ = users['other']
    res = client.patch(f'/api/v1/transactions/{transaction}/cancel', headers=other_headers)
    assert res.status_code == 403


def test_cancel_completed_transaction_invalid(client, users, completed_transaction):
    """Cannot cancel a COMPLETED transaction."""
    buyer_headers, _ = users['buyer']
    res = client.patch(f'/api/v1/transactions/{completed_transaction}/cancel', headers=buyer_headers)
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'INVALID_TRANSITION'


def test_cancel_unauthenticated(client, transaction):
    res = client.patch(f'/api/v1/transactions/{transaction}/cancel')
    assert res.status_code == 401


def test_cancel_not_found(client, users):
    buyer_headers, _ = users['buyer']
    res = client.patch(f'/api/v1/transactions/{str(ObjectId())}/cancel', headers=buyer_headers)
    assert res.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# History and Detail
# ─────────────────────────────────────────────────────────────────────────────

def test_buyer_transaction_history(client, users, transaction):
    """Buyer can retrieve their own transaction list."""
    buyer_headers, buyer_id = users['buyer']
    res = client.get('/api/v1/transactions/mine', headers=buyer_headers)
    assert res.status_code == 200
    items = res.get_json()['data']['items']
    assert len(items) >= 1
    assert all(t['buyer_id'] == buyer_id for t in items)


def test_seller_transaction_history(client, users, transaction):
    """Seller can retrieve their received transaction list."""
    seller_headers, seller_id = users['seller']
    res = client.get('/api/v1/transactions/received', headers=seller_headers)
    assert res.status_code == 200
    items = res.get_json()['data']['items']
    assert len(items) >= 1
    assert all(t['seller_id'] == seller_id for t in items)


def test_transaction_detail_buyer(client, users, transaction):
    """Buyer can view their transaction detail."""
    buyer_headers, _ = users['buyer']
    res = client.get(f'/api/v1/transactions/{transaction}', headers=buyer_headers)
    assert res.status_code == 200
    assert res.get_json()['data']['_id'] == transaction


def test_transaction_detail_seller(client, users, transaction):
    """Seller can view transaction detail for their product."""
    seller_headers, _ = users['seller']
    res = client.get(f'/api/v1/transactions/{transaction}', headers=seller_headers)
    assert res.status_code == 200


def test_transaction_detail_other_user_forbidden(client, users, transaction):
    """Unrelated user cannot view transaction detail."""
    other_headers, _ = users['other']
    res = client.get(f'/api/v1/transactions/{transaction}', headers=other_headers)
    assert res.status_code == 403


def test_transaction_detail_unauthenticated(client, transaction):
    res = client.get(f'/api/v1/transactions/{transaction}')
    assert res.status_code == 401


def test_transaction_detail_not_found(client, users):
    buyer_headers, _ = users['buyer']
    res = client.get(f'/api/v1/transactions/{str(ObjectId())}', headers=buyer_headers)
    assert res.status_code == 404


def test_history_unauthenticated_mine(client):
    res = client.get('/api/v1/transactions/mine')
    assert res.status_code == 401


def test_history_unauthenticated_received(client):
    res = client.get('/api/v1/transactions/received')
    assert res.status_code == 401


# ─────────────────────────────────────────────────────────────────────────────
# Invalid Transition Guards
# ─────────────────────────────────────────────────────────────────────────────

def test_cannot_reserve_cancelled_transaction(client, users, transaction):
    """Cannot reserve a CANCELLED transaction."""
    buyer_headers,  _ = users['buyer']
    seller_headers, _ = users['seller']
    client.patch(f'/api/v1/transactions/{transaction}/cancel', headers=buyer_headers)
    res = client.patch(f'/api/v1/transactions/{transaction}/reserve', headers=seller_headers)
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'INVALID_TRANSITION'


def test_sold_product_cannot_be_reserved_again(client, users, completed_transaction, product):
    """After a transaction completes and product is SOLD, try_reserve on a SOLD product returns False."""
    from backend.models.product import ProductModel
    db          = backend.db.get_db()
    product_doc = db.products.find_one({'_id': ObjectId(product)})
    assert product_doc['status'] == 'SOLD'
    # Attempting to reserve a SOLD product should fail
    result = ProductModel.try_reserve(product)
    assert result is False
