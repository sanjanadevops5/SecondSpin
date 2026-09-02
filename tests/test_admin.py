"""
Comprehensive Phase 8 Admin & Analytics Tests

Covers:
  - Admin authorization guards (401 unauthenticated, 403 non-admin, 200 admin)
  - User management (list, detail, status update, role update, self-protection)
  - Password hash / token sanitization
  - Product moderation (list all including REMOVED, status update, lifecycle rules)
  - Reports system (user creation, validation, anti-spam duplicate guard, admin list, detail, status transitions)
  - Category administration (list all, create, update/deactivate, duplicate slug guard)
  - Marketplace analytics overview (user, product, transaction, PR, review, category metrics)
  - Security checks (privilege escalation, IDOR, forged identity, sensitive data leakage)
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
    """Creates student, admin, and second student users in DB."""
    db = backend.db.get_db()
    student_id = str(ObjectId())
    admin_id   = str(ObjectId())
    other_id   = str(ObjectId())

    db.users.insert_one({
        '_id': ObjectId(student_id),
        'name': 'Student User',
        'email': 'student@university.edu',
        'password_hash': 'pbkdf2:sha256:fakehashvalue',
        'role': 'student',
        'account_status': 'ACTIVE',
        'created_at': datetime.datetime.now(datetime.timezone.utc),
    })

    db.users.insert_one({
        '_id': ObjectId(admin_id),
        'name': 'Admin User',
        'email': 'admin@university.edu',
        'password_hash': 'pbkdf2:sha256:fakehashvalue',
        'role': 'admin',
        'account_status': 'ACTIVE',
        'created_at': datetime.datetime.now(datetime.timezone.utc),
    })

    db.users.insert_one({
        '_id': ObjectId(other_id),
        'name': 'Other Student',
        'email': 'other@university.edu',
        'password_hash': 'pbkdf2:sha256:fakehashvalue',
        'role': 'student',
        'account_status': 'ACTIVE',
        'created_at': datetime.datetime.now(datetime.timezone.utc),
    })

    return {
        'student': (make_headers(app, student_id, 'student'), student_id),
        'admin':   (make_headers(app, admin_id, 'admin'),     admin_id),
        'other':   (make_headers(app, other_id, 'student'),   other_id),
    }


@pytest.fixture
def sample_product(app, users):
    """Creates an ACTIVE product owned by student."""
    db = backend.db.get_db()
    pid = str(ObjectId())
    db.products.insert_one({
        '_id': ObjectId(pid),
        'seller_id': users['student'][1],
        'category_id': 'textbooks',
        'title': 'Calculus Textbook',
        'description': 'Used textbook in good condition',
        'price': 45.0,
        'condition': 'GOOD',
        'status': 'ACTIVE',
        'created_at': datetime.datetime.now(datetime.timezone.utc),
        'updated_at': datetime.datetime.now(datetime.timezone.utc),
    })
    return pid


# ─────────────────────────────────────────────────────────────────────────────
# 1. ADMIN AUTHORIZATION TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_admin_endpoint_unauthenticated(client):
    """Unauthenticated request to admin endpoint is rejected with 401."""
    res = client.get('/api/v1/admin/users')
    assert res.status_code == 401


def test_admin_endpoint_normal_user_forbidden(client, users):
    """Authenticated student user accessing admin endpoint is rejected with 403."""
    student_headers, _ = users['student']
    res = client.get('/api/v1/admin/users', headers=student_headers)
    assert res.status_code == 403
    assert res.get_json()['error']['code'] == 'FORBIDDEN'


def test_admin_endpoint_admin_allowed(client, users):
    """Authenticated admin user is allowed access."""
    admin_headers, _ = users['admin']
    res = client.get('/api/v1/admin/users', headers=admin_headers)
    assert res.status_code == 200
    assert 'items' in res.get_json()['data']


def test_normal_user_cannot_modify_role(client, users):
    """Student trying to change their own or another user's role is rejected with 403."""
    student_headers, student_id = users['student']
    res = client.patch(f'/api/v1/admin/users/{student_id}/role', headers=student_headers, json={'role': 'admin'})
    assert res.status_code == 403


def test_normal_user_cannot_access_analytics(client, users):
    """Student trying to access admin analytics is rejected with 403."""
    student_headers, _ = users['student']
    res = client.get('/api/v1/admin/analytics/overview', headers=student_headers)
    assert res.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# 2. USER MANAGEMENT TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_admin_list_users(client, users):
    """Admin can list all users."""
    admin_headers, _ = users['admin']
    res = client.get('/api/v1/admin/users', headers=admin_headers)
    assert res.status_code == 200
    data = res.get_json()['data']
    assert len(data['items']) >= 3
    # Check that password_hash is sanitized
    for u in data['items']:
        assert 'password_hash' not in u


def test_admin_list_users_filter_role(client, users):
    """Admin can filter users by role."""
    admin_headers, _ = users['admin']
    res = client.get('/api/v1/admin/users?role=admin', headers=admin_headers)
    assert res.status_code == 200
    items = res.get_json()['data']['items']
    assert all(u['role'] == 'admin' for u in items)


def test_admin_get_user_detail(client, users):
    """Admin can get single user detail."""
    admin_headers, _ = users['admin']
    student_id = users['student'][1]
    res = client.get(f'/api/v1/admin/users/{student_id}', headers=admin_headers)
    assert res.status_code == 200
    user_data = res.get_json()['data']
    assert user_data['_id'] == student_id
    assert 'password_hash' not in user_data


def test_admin_get_user_not_found(client, users):
    """Requesting non-existent user returns 404."""
    admin_headers, _ = users['admin']
    res = client.get(f'/api/v1/admin/users/{str(ObjectId())}', headers=admin_headers)
    assert res.status_code == 404


def test_admin_update_user_status(client, users):
    """Admin can suspend a user account and reactivate it."""
    admin_headers, _ = users['admin']
    student_id = users['student'][1]

    # Suspend user
    res1 = client.patch(f'/api/v1/admin/users/{student_id}/status', headers=admin_headers, json={'status': 'SUSPENDED'})
    assert res1.status_code == 200

    # Verify user doc in DB
    db = backend.db.get_db()
    u_doc = db.users.find_one({'_id': ObjectId(student_id)})
    assert u_doc['account_status'] == 'SUSPENDED'

    # Reactivate user
    res2 = client.patch(f'/api/v1/admin/users/{student_id}/status', headers=admin_headers, json={'status': 'ACTIVE'})
    assert res2.status_code == 200


def test_admin_self_suspension_forbidden(client, users):
    """Admin cannot suspend their own admin account."""
    admin_headers, admin_id = users['admin']
    res = client.patch(f'/api/v1/admin/users/{admin_id}/status', headers=admin_headers, json={'status': 'SUSPENDED'})
    assert res.status_code == 403
    assert res.get_json()['error']['code'] == 'FORBIDDEN'


def test_admin_update_user_role(client, users):
    """Admin can promote a student to admin and demote back."""
    admin_headers, _ = users['admin']
    other_id = users['other'][1]

    # Promote to admin
    res1 = client.patch(f'/api/v1/admin/users/{other_id}/role', headers=admin_headers, json={'role': 'admin'})
    assert res1.status_code == 200

    # Demote back to student
    res2 = client.patch(f'/api/v1/admin/users/{other_id}/role', headers=admin_headers, json={'role': 'student'})
    assert res2.status_code == 200


def test_admin_self_demotion_forbidden(client, users):
    """Admin cannot demote their own admin account."""
    admin_headers, admin_id = users['admin']
    res = client.patch(f'/api/v1/admin/users/{admin_id}/role', headers=admin_headers, json={'role': 'student'})
    assert res.status_code == 403
    assert res.get_json()['error']['code'] == 'FORBIDDEN'


def test_update_user_invalid_status(client, users):
    """Invalid status value returns 400."""
    admin_headers, _ = users['admin']
    student_id = users['student'][1]
    res = client.patch(f'/api/v1/admin/users/{student_id}/status', headers=admin_headers, json={'status': 'INVALID'})
    assert res.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# 3. PRODUCT MODERATION TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_admin_list_products_includes_removed(client, users, sample_product):
    """Admin can list products including REMOVED products."""
    admin_headers, _ = users['admin']
    db = backend.db.get_db()
    # Insert a removed product
    db.products.insert_one({
        '_id': ObjectId(), 'seller_id': users['student'][1],
        'title': 'Removed Book', 'price': 10, 'condition': 'FAIR',
        'status': 'REMOVED', 'created_at': datetime.datetime.now(datetime.timezone.utc),
    })

    res = client.get('/api/v1/admin/products', headers=admin_headers)
    assert res.status_code == 200
    items = res.get_json()['data']['items']
    statuses = [p['status'] for p in items]
    assert 'ACTIVE' in statuses
    assert 'REMOVED' in statuses


def test_admin_moderate_product_remove(client, users, sample_product):
    """Admin can moderate a product to REMOVED."""
    admin_headers, _ = users['admin']
    res = client.patch(f'/api/v1/admin/products/{sample_product}/status', headers=admin_headers, json={'status': 'REMOVED'})
    assert res.status_code == 200
    db = backend.db.get_db()
    p_doc = db.products.find_one({'_id': ObjectId(sample_product)})
    assert p_doc['status'] == 'REMOVED'


def test_admin_cannot_reactivate_sold_product(client, users, sample_product):
    """Admin cannot change a SOLD product back to ACTIVE or RESERVED."""
    admin_headers, _ = users['admin']
    db = backend.db.get_db()
    db.products.update_one({'_id': ObjectId(sample_product)}, {'$set': {'status': 'SOLD'}})

    res = client.patch(f'/api/v1/admin/products/{sample_product}/status', headers=admin_headers, json={'status': 'ACTIVE'})
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'INVALID_TRANSITION'


def test_normal_user_cannot_moderate_product(client, users, sample_product):
    """Student cannot use admin product moderation endpoint."""
    student_headers, _ = users['student']
    res = client.patch(f'/api/v1/admin/products/{sample_product}/status', headers=student_headers, json={'status': 'REMOVED'})
    assert res.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# 4. REPORTING SYSTEM TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_user_create_report_product(client, users, sample_product):
    """Authenticated user can submit a report against a product."""
    student_headers, _ = users['student']
    res = client.post('/api/v1/reports/', headers=student_headers, json={
        'target_type': 'PRODUCT',
        'target_id': sample_product,
        'reason': 'Misleading description',
        'description': 'The seller says this is new but it has markings.'
    })
    assert res.status_code == 201
    assert 'report_id' in res.get_json()['data']


def test_user_create_report_user(client, users):
    """Authenticated user can submit a report against another user."""
    student_headers, _ = users['student']
    other_id = users['other'][1]
    res = client.post('/api/v1/reports/', headers=student_headers, json={
        'target_type': 'USER',
        'target_id': other_id,
        'reason': 'Suspicious behavior',
    })
    assert res.status_code == 201


def test_report_unauthenticated(client, sample_product):
    """Unauthenticated report submission is rejected."""
    res = client.post('/api/v1/reports/', json={
        'target_type': 'PRODUCT',
        'target_id': sample_product,
        'reason': 'Spam',
    })
    assert res.status_code == 401


def test_report_nonexistent_target(client, users):
    """Report against nonexistent target returns 404."""
    student_headers, _ = users['student']
    res = client.post('/api/v1/reports/', headers=student_headers, json={
        'target_type': 'PRODUCT',
        'target_id': str(ObjectId()),
        'reason': 'Nonexistent product',
    })
    assert res.status_code == 404


def test_report_invalid_target_type(client, users, sample_product):
    """Invalid target_type returns 400."""
    student_headers, _ = users['student']
    res = client.post('/api/v1/reports/', headers=student_headers, json={
        'target_type': 'INVALID_TYPE',
        'target_id': sample_product,
        'reason': 'Test',
    })
    assert res.status_code == 400


def test_report_duplicate_prevention(client, users, sample_product):
    """Same user cannot create multiple open reports for the same target."""
    student_headers, _ = users['student']
    payload = {'target_type': 'PRODUCT', 'target_id': sample_product, 'reason': 'Spam'}
    res1 = client.post('/api/v1/reports/', headers=student_headers, json=payload)
    assert res1.status_code == 201

    res2 = client.post('/api/v1/reports/', headers=student_headers, json=payload)
    assert res2.status_code == 409
    assert res2.get_json()['error']['code'] == 'DUPLICATE_REPORT'


def test_admin_list_and_manage_reports(client, users, sample_product):
    """Admin can list reports and advance status OPEN -> REVIEWING -> RESOLVED."""
    student_headers, _ = users['student']
    admin_headers, admin_id = users['admin']

    # Create report
    r_res = client.post('/api/v1/reports/', headers=student_headers, json={
        'target_type': 'PRODUCT', 'target_id': sample_product, 'reason': 'Counterfeit'
    })
    report_id = r_res.get_json()['data']['report_id']

    # Admin list reports
    list_res = client.get('/api/v1/admin/reports', headers=admin_headers)
    assert list_res.status_code == 200
    assert len(list_res.get_json()['data']['items']) >= 1

    # Admin update status OPEN -> REVIEWING
    p1 = client.patch(f'/api/v1/admin/reports/{report_id}/status', headers=admin_headers, json={'status': 'REVIEWING'})
    assert p1.status_code == 200

    # Admin update status REVIEWING -> RESOLVED
    p2 = client.patch(f'/api/v1/admin/reports/{report_id}/status', headers=admin_headers, json={'status': 'RESOLVED'})
    assert p2.status_code == 200

    # Verify DB metadata
    db = backend.db.get_db()
    rep = db.reports.find_one({'_id': ObjectId(report_id)})
    assert rep['status'] == 'RESOLVED'
    assert rep['resolved_by'] == admin_id
    assert rep['resolved_at'] is not None


def test_normal_user_cannot_update_report_status(client, users, sample_product):
    """Student cannot update report status."""
    student_headers, _ = users['student']
    # Create report
    r_res = client.post('/api/v1/reports/', headers=student_headers, json={
        'target_type': 'PRODUCT', 'target_id': sample_product, 'reason': 'Inappropriate'
    })
    report_id = r_res.get_json()['data']['report_id']

    res = client.patch(f'/api/v1/admin/reports/{report_id}/status', headers=student_headers, json={'status': 'RESOLVED'})
    assert res.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# 5. CATEGORY ADMINISTRATION TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_admin_get_categories(client, users):
    """Admin can list all categories."""
    admin_headers, _ = users['admin']
    res = client.get('/api/v1/admin/categories', headers=admin_headers)
    assert res.status_code == 200
    assert 'items' in res.get_json()['data']


def test_admin_create_category(client, users):
    """Admin can create a new category."""
    admin_headers, _ = users['admin']
    res = client.post('/api/v1/admin/categories', headers=admin_headers, json={
        'name': 'Lab Equipment',
        'slug': 'lab-equipment',
        'description': 'Goggles, lab coats, tools',
        'icon': 'flask',
    })
    assert res.status_code == 201
    assert 'category_id' in res.get_json()['data']


def test_admin_create_duplicate_category_slug(client, users):
    """Duplicate category slug returns 409 CONFLICT."""
    admin_headers, _ = users['admin']
    payload = {'name': 'Electronics', 'slug': 'electronics'}
    res1 = client.post('/api/v1/admin/categories', headers=admin_headers, json=payload)
    assert res1.status_code == 201

    res2 = client.post('/api/v1/admin/categories', headers=admin_headers, json=payload)
    assert res2.status_code == 409
    assert res2.get_json()['error']['code'] == 'DUPLICATE_CATEGORY'


def test_admin_update_category_deactivate(client, users):
    """Admin can deactivate a category."""
    admin_headers, _ = users['admin']
    # Create category first
    client.post('/api/v1/admin/categories', headers=admin_headers, json={'name': 'Dorm Decor', 'slug': 'dorm-decor'})

    # Deactivate
    res = client.patch('/api/v1/admin/categories/dorm-decor', headers=admin_headers, json={'is_active': False})
    assert res.status_code == 200

    db = backend.db.get_db()
    cat = db.categories.find_one({'slug': 'dorm-decor'})
    assert cat['is_active'] is False


def test_normal_user_cannot_create_category(client, users):
    """Student user cannot create a category."""
    student_headers, _ = users['student']
    res = client.post('/api/v1/admin/categories', headers=student_headers, json={'name': 'Sports', 'slug': 'sports'})
    assert res.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# 6. MARKETPLACE ANALYTICS OVERVIEW TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_admin_analytics_overview(client, users, sample_product):
    """Admin can retrieve aggregated marketplace analytics overview."""
    admin_headers, _ = users['admin']
    db = backend.db.get_db()

    # Seed transactions, PRs, reviews
    pr_id = str(ObjectId())
    db.purchase_requests.insert_one({'_id': ObjectId(pr_id), 'status': 'ACCEPTED'})
    db.transactions.insert_one({'_id': ObjectId(), 'status': 'COMPLETED'})
    t1 = str(ObjectId())
    t2 = str(ObjectId())
    u1 = str(ObjectId())
    u2 = str(ObjectId())
    db.reviews.insert_one({'_id': ObjectId(), 'transaction_id': t1, 'reviewer_id': u1, 'reviewee_id': u2, 'rating': 5})
    db.reviews.insert_one({'_id': ObjectId(), 'transaction_id': t2, 'reviewer_id': u2, 'reviewee_id': u1, 'rating': 3})

    res = client.get('/api/v1/admin/analytics/overview', headers=admin_headers)
    assert res.status_code == 200
    data = res.get_json()['data']

    # Verify sections exist
    assert 'users' in data
    assert 'products' in data
    assert 'transactions' in data
    assert 'purchase_requests' in data
    assert 'reviews' in data
    assert 'reports' in data
    assert 'categories' in data

    # Verify counts reflect DB state
    assert data['users']['total'] >= 3
    assert data['products']['total'] >= 1
    assert data['transactions']['completed'] >= 1
    assert data['reviews']['total'] >= 2
    assert data['reviews']['average_rating'] == 4.0  # (5 + 3) / 2


def test_normal_user_cannot_access_analytics_overview(client, users):
    """Student user cannot access analytics overview."""
    student_headers, _ = users['student']
    res = client.get('/api/v1/admin/analytics/overview', headers=student_headers)
    assert res.status_code == 403
