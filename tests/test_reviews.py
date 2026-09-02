"""
Comprehensive Phase 7 Review Tests

Covers:
  - Valid buyer → seller review
  - Valid seller → buyer review
  - All unauthenticated cases
  - Non-existent transaction
  - Transaction not COMPLETED (PENDING / RESERVED / CANCELLED)
  - Unrelated user cannot review
  - Self-review blocked
  - Duplicate review blocked
  - Rating validation: 0, 6, negative, decimal, boolean, string, missing
  - Comment validation: wrong type, excessive length
  - Client-side field manipulation: reviewer_id, reviewee_id, product_id injections
  - Review retrieval: by product, by user, by id
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
            'sub':  user_id,
            'role': role,
            'exp':  datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expires_in),
            'iat':  datetime.datetime.now(datetime.timezone.utc),
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
    db        = backend.db.get_db()
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
def product_id(app, users):
    db         = backend.db.get_db()
    pid        = str(ObjectId())
    seller_id  = users['seller'][1]
    db.products.insert_one({
        '_id': ObjectId(pid), 'seller_id': seller_id,
        'title': 'Test Product', 'price': 50.0, 'condition': 'GOOD',
        'status': 'SOLD',
        'created_at': datetime.datetime.now(datetime.timezone.utc),
        'updated_at': datetime.datetime.now(datetime.timezone.utc),
    })
    return pid


def _insert_transaction(db, product_id, buyer_id, seller_id, status='COMPLETED'):
    txn_id = str(ObjectId())
    db.transactions.insert_one({
        '_id':                ObjectId(txn_id),
        'purchase_request_id': str(ObjectId()),
        'product_id':         product_id,
        'buyer_id':           buyer_id,
        'seller_id':          seller_id,
        'status':             status,
        'created_at':         datetime.datetime.now(datetime.timezone.utc),
        'updated_at':         datetime.datetime.now(datetime.timezone.utc),
        'completed_at':       datetime.datetime.now(datetime.timezone.utc) if status == 'COMPLETED' else None,
        'cancelled_at':       datetime.datetime.now(datetime.timezone.utc) if status == 'CANCELLED' else None,
    })
    return txn_id


@pytest.fixture
def completed_txn(app, users, product_id):
    """A COMPLETED transaction between buyer and seller."""
    db = backend.db.get_db()
    return _insert_transaction(db, product_id, users['buyer'][1], users['seller'][1], 'COMPLETED')


@pytest.fixture
def pending_txn(app, users, product_id):
    db = backend.db.get_db()
    return _insert_transaction(db, product_id, users['buyer'][1], users['seller'][1], 'PENDING')


@pytest.fixture
def reserved_txn(app, users, product_id):
    db = backend.db.get_db()
    return _insert_transaction(db, product_id, users['buyer'][1], users['seller'][1], 'RESERVED')


@pytest.fixture
def cancelled_txn(app, users, product_id):
    db = backend.db.get_db()
    return _insert_transaction(db, product_id, users['buyer'][1], users['seller'][1], 'CANCELLED')


# ─────────────────────────────────────────────────────────────────────────────
# Valid Review Creation
# ─────────────────────────────────────────────────────────────────────────────

def test_buyer_reviews_seller(client, users, completed_txn):
    """Buyer can leave a review for the seller on a COMPLETED transaction."""
    buyer_headers, _ = users['buyer']
    seller_id        = users['seller'][1]
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn,
        'reviewee_id':    seller_id,
        'rating':         5,
        'comment':        'Great seller!',
    })
    assert res.status_code == 201
    assert 'review_id' in res.get_json()['data']


def test_seller_reviews_buyer(client, users, completed_txn):
    """Seller can leave a review for the buyer on a COMPLETED transaction."""
    seller_headers, _ = users['seller']
    buyer_id           = users['buyer'][1]
    res = client.post('/api/v1/reviews/', headers=seller_headers, json={
        'transaction_id': completed_txn,
        'reviewee_id':    buyer_id,
        'rating':         4,
        'comment':        'Smooth transaction.',
    })
    assert res.status_code == 201


def test_review_without_comment(client, users, completed_txn):
    """Comment is optional — omitting it is valid."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn,
        'reviewee_id':    users['seller'][1],
        'rating':         3,
    })
    assert res.status_code == 201


def test_review_rating_min(client, users, completed_txn):
    """Rating of 1 (minimum) is accepted."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn,
        'reviewee_id':    users['seller'][1],
        'rating':         1,
    })
    assert res.status_code == 201


def test_review_rating_max(client, users, completed_txn):
    """Rating of 5 (maximum) is accepted."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn,
        'reviewee_id':    users['seller'][1],
        'rating':         5,
    })
    assert res.status_code == 201


# ─────────────────────────────────────────────────────────────────────────────
# Authentication
# ─────────────────────────────────────────────────────────────────────────────

def test_review_unauthenticated(client, users, completed_txn):
    """Unauthenticated request is rejected with 401."""
    res = client.post('/api/v1/reviews/', json={
        'transaction_id': completed_txn,
        'reviewee_id':    users['seller'][1],
        'rating':         4,
    })
    assert res.status_code == 401


# ─────────────────────────────────────────────────────────────────────────────
# Transaction Eligibility
# ─────────────────────────────────────────────────────────────────────────────

def test_review_transaction_not_found(client, users):
    """Non-existent transaction_id returns 404."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': str(ObjectId()),
        'reviewee_id':    users['seller'][1],
        'rating':         4,
    })
    assert res.status_code == 404


def test_review_pending_transaction(client, users, pending_txn):
    """Cannot review a PENDING transaction."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': pending_txn,
        'reviewee_id':    users['seller'][1],
        'rating':         4,
    })
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'NOT_ELIGIBLE'


def test_review_reserved_transaction(client, users, reserved_txn):
    """Cannot review a RESERVED transaction."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': reserved_txn,
        'reviewee_id':    users['seller'][1],
        'rating':         4,
    })
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'NOT_ELIGIBLE'


def test_review_cancelled_transaction(client, users, cancelled_txn):
    """Cannot review a CANCELLED transaction."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': cancelled_txn,
        'reviewee_id':    users['seller'][1],
        'rating':         4,
    })
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'NOT_ELIGIBLE'


# ─────────────────────────────────────────────────────────────────────────────
# Authorization
# ─────────────────────────────────────────────────────────────────────────────

def test_review_unrelated_user(client, users, completed_txn):
    """An unrelated user cannot review either participant."""
    other_headers, _ = users['other']
    res = client.post('/api/v1/reviews/', headers=other_headers, json={
        'transaction_id': completed_txn,
        'reviewee_id':    users['seller'][1],
        'rating':         3,
    })
    assert res.status_code == 403


def test_review_self_review_buyer(client, users, completed_txn):
    """Buyer cannot review themselves."""
    buyer_headers, buyer_id = users['buyer']
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn,
        'reviewee_id':    buyer_id,
        'rating':         5,
    })
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'SELF_REVIEW'


def test_review_self_review_seller(client, users, completed_txn):
    """Seller cannot review themselves."""
    seller_headers, seller_id = users['seller']
    res = client.post('/api/v1/reviews/', headers=seller_headers, json={
        'transaction_id': completed_txn,
        'reviewee_id':    seller_id,
        'rating':         5,
    })
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'SELF_REVIEW'


def test_review_invalid_reviewee(client, users, completed_txn):
    """Reviewee must be the other party — not an unrelated user."""
    buyer_headers, _ = users['buyer']
    other_id          = users['other'][1]
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn,
        'reviewee_id':    other_id,
        'rating':         4,
    })
    assert res.status_code == 403
    assert res.get_json()['error']['code'] == 'INVALID_REVIEWEE'


def test_review_duplicate_same_direction(client, users, completed_txn):
    """Buyer cannot review the seller twice for the same transaction."""
    buyer_headers, _ = users['buyer']
    payload = {'transaction_id': completed_txn, 'reviewee_id': users['seller'][1], 'rating': 5}
    res1 = client.post('/api/v1/reviews/', headers=buyer_headers, json=payload)
    assert res1.status_code == 201
    res2 = client.post('/api/v1/reviews/', headers=buyer_headers, json=payload)
    assert res2.status_code == 409
    assert res2.get_json()['error']['code'] == 'DUPLICATE_REVIEW'


def test_both_parties_can_each_review(client, users, completed_txn):
    """Buyer and seller may each submit one review (different directions)."""
    buyer_headers,  buyer_id  = users['buyer']
    seller_headers, seller_id = users['seller']
    r1 = client.post('/api/v1/reviews/', headers=buyer_headers,
                     json={'transaction_id': completed_txn, 'reviewee_id': seller_id, 'rating': 4})
    r2 = client.post('/api/v1/reviews/', headers=seller_headers,
                     json={'transaction_id': completed_txn, 'reviewee_id': buyer_id, 'rating': 5})
    assert r1.status_code == 201
    assert r2.status_code == 201


# ─────────────────────────────────────────────────────────────────────────────
# Rating Validation
# ─────────────────────────────────────────────────────────────────────────────

def test_rating_zero(client, users, completed_txn):
    """Rating of 0 is rejected."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn, 'reviewee_id': users['seller'][1], 'rating': 0})
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'INVALID_RATING'


def test_rating_six(client, users, completed_txn):
    """Rating of 6 is rejected."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn, 'reviewee_id': users['seller'][1], 'rating': 6})
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'INVALID_RATING'


def test_rating_negative(client, users, completed_txn):
    """Negative rating is rejected."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn, 'reviewee_id': users['seller'][1], 'rating': -1})
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'INVALID_RATING'


def test_rating_decimal(client, users, completed_txn):
    """Decimal rating (float) is rejected — must be integer."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn, 'reviewee_id': users['seller'][1], 'rating': 4.5})
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'INVALID_RATING'


def test_rating_string(client, users, completed_txn):
    """String rating is rejected."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn, 'reviewee_id': users['seller'][1], 'rating': '5'})
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'INVALID_RATING'


def test_rating_boolean_true(client, users, completed_txn):
    """Boolean True (which is a subclass of int in Python) is rejected."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn, 'reviewee_id': users['seller'][1], 'rating': True})
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'INVALID_RATING'


def test_rating_missing_from_body(client, users, completed_txn):
    """Missing rating field returns 422 (required field check)."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn, 'reviewee_id': users['seller'][1]})
    assert res.status_code == 422


def test_rating_null(client, users, completed_txn):
    """null/None rating is rejected."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn, 'reviewee_id': users['seller'][1], 'rating': None})
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'INVALID_RATING'


# ─────────────────────────────────────────────────────────────────────────────
# Comment Validation
# ─────────────────────────────────────────────────────────────────────────────

def test_comment_too_long(client, users, completed_txn):
    """Comment exceeding 1000 characters is rejected."""
    buyer_headers, _ = users['buyer']
    long_comment      = 'x' * 1001
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn,
        'reviewee_id':    users['seller'][1],
        'rating':         4,
        'comment':        long_comment,
    })
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'COMMENT_TOO_LONG'


def test_comment_wrong_type(client, users, completed_txn):
    """Comment must be a string — integer is rejected."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn,
        'reviewee_id':    users['seller'][1],
        'rating':         4,
        'comment':        12345,
    })
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'INVALID_COMMENT'


def test_comment_max_length_exact(client, users, completed_txn):
    """Comment of exactly 1000 characters is accepted."""
    buyer_headers, _ = users['buyer']
    exact_comment     = 'a' * 1000
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn,
        'reviewee_id':    users['seller'][1],
        'rating':         3,
        'comment':        exact_comment,
    })
    assert res.status_code == 201


# ─────────────────────────────────────────────────────────────────────────────
# Manipulation Prevention
# ─────────────────────────────────────────────────────────────────────────────

def test_reviewer_id_from_auth_not_body(client, users, completed_txn):
    """
    reviewer_id is always derived from the JWT — a different reviewer_id in the body is ignored.
    The test verifies the stored reviewer_id matches g.user_id (buyer), not the injected value.
    """
    buyer_headers, buyer_id = users['buyer']
    fake_reviewer_id         = str(ObjectId())
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn,
        'reviewee_id':    users['seller'][1],
        'rating':         4,
        'reviewer_id':    fake_reviewer_id,  # should be ignored
    })
    assert res.status_code == 201
    review_id = res.get_json()['data']['review_id']
    db        = backend.db.get_db()
    review    = db.reviews.find_one({'_id': ObjectId(review_id)})
    assert review['reviewer_id'] == buyer_id
    assert review['reviewer_id'] != fake_reviewer_id


def test_product_id_derived_from_transaction_not_body(client, users, completed_txn, product_id):
    """product_id is derived from the transaction; any client-supplied product_id is ignored."""
    buyer_headers, _ = users['buyer']
    fake_product_id   = str(ObjectId())
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn,
        'reviewee_id':    users['seller'][1],
        'rating':         5,
        'product_id':     fake_product_id,  # should be ignored
    })
    assert res.status_code == 201
    review_id = res.get_json()['data']['review_id']
    db        = backend.db.get_db()
    review    = db.reviews.find_one({'_id': ObjectId(review_id)})
    assert review['product_id'] == product_id
    assert review['product_id'] != fake_product_id


def test_missing_required_fields(client, users, completed_txn):
    """Missing transaction_id returns 422."""
    buyer_headers, _ = users['buyer']
    res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'reviewee_id': users['seller'][1], 'rating': 4})
    assert res.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
# Review Retrieval
# ─────────────────────────────────────────────────────────────────────────────

def test_get_reviews_by_product(client, users, completed_txn, product_id):
    """After submitting a review, it appears in the product review list."""
    buyer_headers, _ = users['buyer']
    client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn,
        'reviewee_id':    users['seller'][1],
        'rating':         5,
    })
    res = client.get(f'/api/v1/reviews/product/{product_id}', headers=buyer_headers)
    assert res.status_code == 200
    items = res.get_json()['data']['items']
    assert len(items) == 1
    assert items[0]['product_id'] == product_id


def test_get_reviews_by_user(client, users, completed_txn):
    """After submitting a review, it appears in the reviewee's user review list."""
    buyer_headers, _ = users['buyer']
    seller_id         = users['seller'][1]
    client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn,
        'reviewee_id':    seller_id,
        'rating':         4,
        'comment':        'Reliable seller.',
    })
    res = client.get(f'/api/v1/reviews/user/{seller_id}', headers=buyer_headers)
    assert res.status_code == 200
    items = res.get_json()['data']['items']
    assert len(items) == 1
    assert items[0]['reviewee_id'] == seller_id


def test_get_review_by_id(client, users, completed_txn):
    """Can retrieve a single review by its ID."""
    buyer_headers, _ = users['buyer']
    post_res          = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn,
        'reviewee_id':    users['seller'][1],
        'rating':         3,
        'comment':        'Decent.',
    })
    assert post_res.status_code == 201
    review_id = post_res.get_json()['data']['review_id']
    get_res   = client.get(f'/api/v1/reviews/{review_id}', headers=buyer_headers)
    assert get_res.status_code == 200
    assert get_res.get_json()['data']['_id'] == review_id
    assert get_res.get_json()['data']['rating'] == 3


def test_get_review_not_found(client, users):
    buyer_headers, _ = users['buyer']
    res = client.get(f'/api/v1/reviews/{str(ObjectId())}', headers=buyer_headers)
    assert res.status_code == 404


def test_get_review_unauthenticated(client, users, completed_txn):
    buyer_headers, _ = users['buyer']
    post_res = client.post('/api/v1/reviews/', headers=buyer_headers, json={
        'transaction_id': completed_txn,
        'reviewee_id':    users['seller'][1],
        'rating':         4,
    })
    review_id = post_res.get_json()['data']['review_id']
    res = client.get(f'/api/v1/reviews/{review_id}')
    assert res.status_code == 401
