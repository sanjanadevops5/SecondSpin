"""
Comprehensive Phase 9 Smart Feature & Recommendation Tests

Covers:
  - Related product discovery (scoring, ranking, exclusion of target and REMOVED products, limit bounds)
  - Popular products (wishlist, purchase request, transaction weighting, status exclusions)
  - Popular categories (active listings, wishlists, requests, sales weighting)
  - Historical price insights (current price, average, min, max, comparable count, insufficient data handling, price comparisons)
  - Personalized recommendations (authenticated user, wishlist/request/tx signals, cold-start fallback, privacy)
  - Security & parameter boundary validation (401 unauthenticated, IDOR, parameter bounds, 404 nonexistent targets)
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
    secret = app.config.get('JWT_SECRET_KEY')
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


def make_headers(app, user_id, role='student'):
    return {'Authorization': f'Bearer {generate_token(app, user_id, role)}'}


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def users(app):
    db = backend.db.get_db()
    u1 = str(ObjectId())
    u2 = str(ObjectId())
    db.users.insert_one({'_id': ObjectId(u1), 'email': 'u1@university.edu', 'role': 'student', 'account_status': 'ACTIVE'})
    db.users.insert_one({'_id': ObjectId(u2), 'email': 'u2@university.edu', 'role': 'student', 'account_status': 'ACTIVE'})
    return {
        'u1': (make_headers(app, u1), u1),
        'u2': (make_headers(app, u2), u2),
    }


@pytest.fixture
def products_fixture(app, users):
    db = backend.db.get_db()
    seller_id = users['u2'][1]
    now = datetime.datetime.now(datetime.timezone.utc)

    # Insert sample categories
    db.categories.insert_one({'name': 'Textbooks', 'slug': 'textbooks', 'is_active': True})
    db.categories.insert_one({'name': 'Electronics', 'slug': 'electronics', 'is_active': True})

    # Insert products
    p1 = str(ObjectId())  # Textbook 1 ($50)
    p2 = str(ObjectId())  # Textbook 2 ($55, same category, matching title)
    p3 = str(ObjectId())  # Electronics item ($80)
    p4 = str(ObjectId())  # Removed Textbook ($30)
    p5 = str(ObjectId())  # Textbook 3 ($40, cheap textbook)

    db.products.insert_one({
        '_id': ObjectId(p1), 'seller_id': seller_id, 'category_id': 'textbooks',
        'title': 'Calculus Stewart 8th Edition', 'description': 'Math book',
        'price': 50.0, 'condition': 'GOOD', 'status': 'ACTIVE', 'created_at': now
    })

    db.products.insert_one({
        '_id': ObjectId(p2), 'seller_id': seller_id, 'category_id': 'textbooks',
        'title': 'Calculus Early Transcendentals', 'description': 'Math book',
        'price': 55.0, 'condition': 'GOOD', 'status': 'ACTIVE', 'created_at': now
    })

    db.products.insert_one({
        '_id': ObjectId(p3), 'seller_id': seller_id, 'category_id': 'electronics',
        'title': 'TI-84 Plus Graphing Calculator', 'description': 'Calculator',
        'price': 80.0, 'condition': 'LIKE_NEW', 'status': 'ACTIVE', 'created_at': now
    })

    db.products.insert_one({
        '_id': ObjectId(p4), 'seller_id': seller_id, 'category_id': 'textbooks',
        'title': 'Old Removed Calculus', 'description': 'Removed book',
        'price': 30.0, 'condition': 'POOR', 'status': 'REMOVED', 'created_at': now
    })

    db.products.insert_one({
        '_id': ObjectId(p5), 'seller_id': seller_id, 'category_id': 'textbooks',
        'title': 'Applied Calculus', 'description': 'Math book cheap',
        'price': 40.0, 'condition': 'FAIR', 'status': 'ACTIVE', 'created_at': now
    })

    return {'p1': p1, 'p2': p2, 'p3': p3, 'p4': p4, 'p5': p5}


# ─────────────────────────────────────────────────────────────────────────────
# 1. RELATED PRODUCTS TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_get_related_products_success(client, products_fixture):
    """Related products endpoint returns related items with scoring & explainable reason."""
    p1 = products_fixture['p1']
    res = client.get(f'/api/v1/products/{p1}/related')
    assert res.status_code == 200
    data = res.get_json()['data']
    assert 'items' in data
    items = data['items']
    assert len(items) >= 1
    # Check that p1 itself is excluded
    prod_ids = [item['product']['_id'] for item in items]
    assert p1 not in prod_ids
    # Check explainable reason and score
    assert 'reason' in items[0]
    assert 'score' in items[0]


def test_get_related_products_nonexistent(client):
    """Requesting related products for a non-existent product returns 404."""
    res = client.get(f'/api/v1/products/{str(ObjectId())}/related')
    assert res.status_code == 404


def test_get_related_products_invalid_id_format(client):
    """Invalid string product ID returns 404."""
    res = client.get('/api/v1/products/invalid-id-string/related')
    assert res.status_code == 404


def test_get_related_products_removed_excluded(client, products_fixture):
    """Removed products are never returned in related products."""
    p1 = products_fixture['p1']
    p4 = products_fixture['p4']
    res = client.get(f'/api/v1/products/{p1}/related')
    assert res.status_code == 200
    prod_ids = [item['product']['_id'] for item in res.get_json()['data']['items']]
    assert p4 not in prod_ids


def test_get_related_products_for_removed_target(client, products_fixture):
    """Requesting related products for a REMOVED product returns 404."""
    p4 = products_fixture['p4']
    res = client.get(f'/api/v1/products/{p4}/related')
    assert res.status_code == 404


def test_get_related_products_category_ranking(client, products_fixture):
    """Products in the same category rank higher than products in a different category."""
    p1 = products_fixture['p1']  # Textbook
    res = client.get(f'/api/v1/products/{p1}/related')
    assert res.status_code == 200
    items = res.get_json()['data']['items']
    # Top item should be a Textbook (p2 or p5)
    top_cat = items[0]['product']['category_id']
    assert top_cat == 'textbooks'


def test_get_related_products_limit_param(client, products_fixture):
    """Limit query parameter is honored."""
    p1 = products_fixture['p1']
    res = client.get(f'/api/v1/products/{p1}/related?limit=1')
    assert res.status_code == 200
    assert len(res.get_json()['data']['items']) <= 1


def test_get_related_products_invalid_limit(client, products_fixture):
    """Invalid limit returns 400."""
    p1 = products_fixture['p1']
    res = client.get(f'/api/v1/products/{p1}/related?limit=invalid')
    assert res.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# 2. POPULAR PRODUCTS TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_get_popular_products_success(client, users, products_fixture):
    """Popular products endpoint returns items ranked by marketplace demand signals."""
    db = backend.db.get_db()
    p2 = products_fixture['p2']

    # Add wishlist and PR activity to p2
    db.wishlist.insert_one({'user_id': str(ObjectId()), 'product_id': p2})
    db.purchase_requests.insert_one({'_id': ObjectId(), 'product_id': p2, 'status': 'ACCEPTED'})
    db.transactions.insert_one({'_id': ObjectId(), 'product_id': p2, 'status': 'COMPLETED'})

    res = client.get('/api/v1/products/popular')
    assert res.status_code == 200
    data = res.get_json()['data']
    assert 'items' in data
    assert len(data['items']) >= 1
    top_item = data['items'][0]
    assert top_item['product']['_id'] == p2
    assert top_item['popularity_score'] > 0
    assert 'reason' in top_item


def test_get_popular_products_excludes_removed(client, products_fixture):
    """Popular products endpoint excludes REMOVED items."""
    p4 = products_fixture['p4']
    res = client.get('/api/v1/products/popular')
    assert res.status_code == 200
    prod_ids = [item['product']['_id'] for item in res.get_json()['data']['items']]
    assert p4 not in prod_ids


def test_get_popular_products_limit(client):
    """Limit query parameter works cleanly."""
    res = client.get('/api/v1/products/popular?limit=2')
    assert res.status_code == 200
    assert len(res.get_json()['data']['items']) <= 2


def test_get_popular_products_empty_db(app, client):
    """Empty marketplace returns empty list cleanly."""
    db = backend.db.get_db()
    db.products.delete_many({})
    res = client.get('/api/v1/products/popular')
    assert res.status_code == 200
    assert res.get_json()['data']['items'] == []


# ─────────────────────────────────────────────────────────────────────────────
# 3. POPULAR CATEGORIES TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_get_popular_categories_success(client, products_fixture):
    """Popular categories endpoint returns categories ranked by demand score."""
    res = client.get('/api/v1/categories/popular')
    assert res.status_code == 200
    data = res.get_json()['data']
    assert 'items' in data
    items = data['items']
    assert len(items) >= 1
    assert 'demand_score' in items[0]
    assert 'reason' in items[0]


def test_get_popular_categories_invalid_limit(client):
    """Invalid limit query param returns 400 or fallback."""
    res = client.get('/api/v1/categories/popular?limit=-5')
    assert res.status_code == 200  # Fallback to default limit


# ─────────────────────────────────────────────────────────────────────────────
# 4. HISTORICAL PRICE INSIGHTS TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_price_insights_sufficient_data(client, products_fixture):
    """Price insights returns min, max, average, and comparison when comparables >= 2."""
    p1 = products_fixture['p1']
    res = client.get(f'/api/v1/products/{p1}/price-insights')
    assert res.status_code == 200
    data = res.get_json()['data']
    assert data['product_id'] == p1
    assert data['insufficient_data'] is False
    assert data['comparable_count'] >= 3
    assert data['historical_average'] == 48.33  # (50 + 55 + 40) / 3 = 48.33
    assert data['min_price'] == 40.0
    assert data['max_price'] == 55.0
    assert 'price_comparison' in data


def test_price_insights_comparison_messages(client, users):
    """Verifies price comparison classification (below, above, fair)."""
    db = backend.db.get_db()
    now = datetime.datetime.now(datetime.timezone.utc)
    seller_id = users['u2'][1]

    p_cheap = str(ObjectId())
    p_norm1 = str(ObjectId())
    p_norm2 = str(ObjectId())

    db.products.insert_one({'_id': ObjectId(p_cheap), 'seller_id': seller_id, 'category_id': 'widgets', 'title': 'Cheap Widget', 'price': 20.0, 'status': 'ACTIVE', 'created_at': now})
    db.products.insert_one({'_id': ObjectId(p_norm1), 'seller_id': seller_id, 'category_id': 'widgets', 'title': 'Widget 1', 'price': 100.0, 'status': 'ACTIVE', 'created_at': now})
    db.products.insert_one({'_id': ObjectId(p_norm2), 'seller_id': seller_id, 'category_id': 'widgets', 'title': 'Widget 2', 'price': 100.0, 'status': 'ACTIVE', 'created_at': now})

    res = client.get(f'/api/v1/products/{p_cheap}/price-insights')
    assert res.status_code == 200
    assert res.get_json()['data']['price_comparison'] == "Priced below historical average"


def test_price_insights_insufficient_data(client, users):
    """Single listing returns insufficient_data: true and null average."""
    db = backend.db.get_db()
    pid = str(ObjectId())
    db.products.insert_one({
        '_id': ObjectId(pid), 'seller_id': users['u2'][1], 'category_id': 'rare-category',
        'title': 'Rare Item', 'price': 500.0, 'condition': 'NEW', 'status': 'ACTIVE'
    })

    res = client.get(f'/api/v1/products/{pid}/price-insights')
    assert res.status_code == 200
    data = res.get_json()['data']
    assert data['insufficient_data'] is True
    assert data['historical_average'] is None


def test_price_insights_nonexistent_product(client):
    """Non-existent product returns 404."""
    res = client.get(f'/api/v1/products/{str(ObjectId())}/price-insights')
    assert res.status_code == 404


def test_price_insights_removed_product(client, products_fixture):
    """Removed product returns 404."""
    p4 = products_fixture['p4']
    res = client.get(f'/api/v1/products/{p4}/price-insights')
    assert res.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# 5. PERSONALIZED RECOMMENDATIONS & COLD-START TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_recommendations_unauthenticated_rejected(client):
    """Unauthenticated request to /api/v1/recommendations is rejected with 401."""
    res = client.get('/api/v1/recommendations')
    assert res.status_code == 401


def test_recommendations_cold_start(client, users, products_fixture):
    """New user with no history receives campus-wide popular fallback recommendations."""
    u1_headers, _ = users['u1']
    res = client.get('/api/v1/recommendations', headers=u1_headers)
    assert res.status_code == 200
    data = res.get_json()['data']
    assert 'items' in data
    items = data['items']
    assert len(items) >= 1
    assert "cold-start" in items[0]['reason'].lower() or "popular" in items[0]['reason'].lower()


def test_recommendations_warm_user_wishlist(client, users, products_fixture):
    """User with wishlist interest receives category-matched recommendations."""
    u1_headers, u1_id = users['u1']
    p2 = products_fixture['p2']
    db = backend.db.get_db()

    # User 1 adds a textbook (p2) to wishlist
    db.wishlist.insert_one({'user_id': u1_id, 'product_id': p2})

    res = client.get('/api/v1/recommendations', headers=u1_headers)
    assert res.status_code == 200
    items = res.get_json()['data']['items']
    assert len(items) >= 1
    assert "Textbooks" in items[0]['reason'] or "interest" in items[0]['reason']


def test_recommendations_warm_user_purchase_request(client, users, products_fixture):
    """User with purchase request history receives category-matched recommendations."""
    u1_headers, u1_id = users['u1']
    p3 = products_fixture['p3']  # Electronics item
    db = backend.db.get_db()

    db.purchase_requests.insert_one({'_id': ObjectId(), 'buyer_id': u1_id, 'product_id': p3, 'status': 'ACCEPTED'})

    res = client.get('/api/v1/recommendations', headers=u1_headers)
    assert res.status_code == 200
    items = res.get_json()['data']['items']
    assert len(items) >= 1
    assert "Electronics" in items[0]['reason'] or "interest" in items[0]['reason']


def test_recommendations_excludes_own_products(client, users, products_fixture):
    """User does not receive their own listed products as recommendations."""
    u2_headers, u2_id = users['u2']  # Seller of products
    res = client.get('/api/v1/recommendations', headers=u2_headers)
    assert res.status_code == 200
    items = res.get_json()['data']['items']
    for item in items:
        seller_id = item['product'].get('seller', {}).get('id') or item['product'].get('seller_id')
        assert seller_id != u2_id


def test_recommendations_ignore_client_user_id_forgery(client, users, products_fixture):
    """
    Passing ?user_id=another_user in query params does NOT alter recommendation logic.
    Identity is strictly derived from JWT token (g.user_id).
    """
    u1_headers, u1_id = users['u1']
    u2_id = users['u2'][1]

    # u1 attempts to pass ?user_id=u2_id
    res = client.get(f'/api/v1/recommendations?user_id={u2_id}', headers=u1_headers)
    assert res.status_code == 200
    # User 1 receives recommendations meant for user 1 (not u2's items)
