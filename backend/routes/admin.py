"""
Admin Blueprint — Phase 8
Provides secure, admin-only endpoints for:
  - User management (list, view, status update, role update)
  - Listing / product moderation
  - User and listing report management
  - Category administration
  - Marketplace analytics overview (aggregated statistics)

All endpoints require JWT auth AND admin role privileges:
  @jwt_required
  @role_required('admin')
"""
from flask import Blueprint, request, g

from backend.responses import success_response, error_response
from backend.validation import validate_json
from backend.auth_middleware import jwt_required, role_required
from backend.models.user import UserModel
from backend.models.product import ProductModel
from backend.models.report import ReportModel
from backend.models.category import CategoryModel
from backend.models.transaction import TransactionModel
from backend.models.purchase_request import PurchaseRequestModel
from backend.models.review import ReviewModel

admin_bp = Blueprint('admin', __name__)


# ===========================================================================
# 1. USER MANAGEMENT
# ===========================================================================

@admin_bp.route('/users', methods=['GET'])
@jwt_required
@role_required('admin')
def get_users():
    """Paginated list of all users with optional role and status filters."""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        if page < 1: page = 1
        if limit < 1: limit = 20
        if limit > 100: limit = 100
    except ValueError:
        return error_response(code='INVALID_PAGINATION', message='Page and limit must be positive integers.', status_code=400)

    role = request.args.get('role')
    account_status = request.args.get('status')

    result = UserModel.get_all(page=page, limit=limit, role=role, account_status=account_status)
    return success_response(data=result)


@admin_bp.route('/users/<user_id>', methods=['GET'])
@jwt_required
@role_required('admin')
def get_user_detail(user_id):
    """Retrieve full detail of a specific user (sanitized, no password_hash)."""
    user = UserModel.get_by_id(user_id)
    if not user:
        return error_response(code='NOT_FOUND', message='User not found.', status_code=404)
    return success_response(data=UserModel.sanitize_user(user))


@admin_bp.route('/users/<user_id>/status', methods=['PATCH'])
@jwt_required
@role_required('admin')
@validate_json(required_fields=['status'])
def update_user_status(user_id):
    """Update a user's account status (ACTIVE or SUSPENDED)."""
    user = UserModel.get_by_id(user_id)
    if not user:
        return error_response(code='NOT_FOUND', message='User not found.', status_code=404)

    data = request.get_json()
    new_status = str(data.get('status', '')).upper().strip()
    if new_status not in ['ACTIVE', 'SUSPENDED']:
        return error_response(code='INVALID_STATUS', message='Status must be ACTIVE or SUSPENDED.', status_code=400)

    # Self-protection: Admin cannot suspend themselves
    if user_id == g.user_id and new_status == 'SUSPENDED':
        return error_response(code='FORBIDDEN', message='You cannot suspend your own admin account.', status_code=403)

    success = UserModel.update_status(user_id, new_status)
    if not success:
        return error_response(code='DATABASE_ERROR', message='Failed to update user status.', status_code=500)

    return success_response(message=f'User status updated to {new_status}.')


@admin_bp.route('/users/<user_id>/role', methods=['PATCH'])
@jwt_required
@role_required('admin')
@validate_json(required_fields=['role'])
def update_user_role(user_id):
    """Update a user's role (student or admin)."""
    user = UserModel.get_by_id(user_id)
    if not user:
        return error_response(code='NOT_FOUND', message='User not found.', status_code=404)

    data = request.get_json()
    new_role = str(data.get('role', '')).lower().strip()
    if new_role not in ['student', 'admin']:
        return error_response(code='INVALID_ROLE', message='Role must be student or admin.', status_code=400)

    # Self-protection: Admin cannot demote themselves
    if user_id == g.user_id and new_role != 'admin':
        return error_response(code='FORBIDDEN', message='You cannot demote your own admin account.', status_code=403)

    success = UserModel.update_role(user_id, new_role)
    if not success:
        return error_response(code='DATABASE_ERROR', message='Failed to update user role.', status_code=500)

    return success_response(message=f'User role updated to {new_role}.')


# ===========================================================================
# 2. LISTING / PRODUCT MODERATION
# ===========================================================================

@admin_bp.route('/products', methods=['GET'])
@jwt_required
@role_required('admin')
def get_admin_products():
    """List products for administration, including REMOVED products."""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        if page < 1: page = 1
        if limit < 1: limit = 20
        if limit > 100: limit = 100
    except ValueError:
        return error_response(code='INVALID_PAGINATION', message='Page and limit must be positive integers.', status_code=400)

    status = request.args.get('status')
    filters = {}
    if status:
        if status not in ProductModel.STATUSES:
            return error_response(code='INVALID_STATUS', message='Invalid status filter.', status_code=400)
        filters['status'] = status
    else:
        # Show all statuses including REMOVED for admin
        filters['status'] = {'$in': ProductModel.STATUSES}

    result = ProductModel.search_products(query_filters=filters, page=page, limit=limit)
    return success_response(data=result)


@admin_bp.route('/products/<product_id>/status', methods=['PATCH'])
@jwt_required
@role_required('admin')
@validate_json(required_fields=['status'])
def moderate_product_status(product_id):
    """Moderate listing status (ACTIVE, RESERVED, SOLD, REMOVED)."""
    product = ProductModel.get_by_id(product_id)
    if not product:
        return error_response(code='NOT_FOUND', message='Product not found.', status_code=404)

    data = request.get_json()
    new_status = str(data.get('status', '')).upper().strip()
    if new_status not in ProductModel.STATUSES:
        return error_response(code='INVALID_STATUS', message=f"Status must be one of: {', '.join(ProductModel.STATUSES)}.", status_code=400)

    current_status = product.get('status')

    # Lifecycle integrity rules:
    # 1. Cannot transition out of SOLD back to ACTIVE or RESERVED
    if current_status == 'SOLD' and new_status in ['ACTIVE', 'RESERVED']:
        return error_response(code='INVALID_TRANSITION', message=f'Cannot transition a SOLD product back to {new_status}.', status_code=400)

    success = ProductModel.update_product(product_id, {'status': new_status})
    if not success:
        return error_response(code='DATABASE_ERROR', message='Failed to update product status.', status_code=500)

    return success_response(message=f'Product status updated to {new_status}.')


# ===========================================================================
# 3. REPORT MANAGEMENT
# ===========================================================================

@admin_bp.route('/reports', methods=['GET'])
@jwt_required
@role_required('admin')
def get_reports():
    """List reports with optional status and target_type filters."""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        if page < 1: page = 1
        if limit < 1: limit = 20
        if limit > 100: limit = 100
    except ValueError:
        return error_response(code='INVALID_PAGINATION', message='Page and limit must be positive integers.', status_code=400)

    status = request.args.get('status')
    target_type = request.args.get('target_type')

    if status and status not in ReportModel.STATUSES:
        return error_response(code='INVALID_STATUS', message='Invalid status filter.', status_code=400)

    if target_type and target_type.upper() not in ReportModel.TARGET_TYPES:
        return error_response(code='INVALID_TARGET_TYPE', message='Invalid target_type filter.', status_code=400)

    result = ReportModel.search_reports(
        status=status,
        target_type=target_type.upper() if target_type else None,
        page=page,
        limit=limit,
    )
    return success_response(data=result)


@admin_bp.route('/reports/<report_id>', methods=['GET'])
@jwt_required
@role_required('admin')
def get_admin_report_detail(report_id):
    """Retrieve full detail of a specific report."""
    report = ReportModel.get_by_id(report_id)
    if not report:
        return error_response(code='NOT_FOUND', message='Report not found.', status_code=404)
    return success_response(data=report)


@admin_bp.route('/reports/<report_id>/status', methods=['PATCH'])
@jwt_required
@role_required('admin')
@validate_json(required_fields=['status'])
def update_report_status(report_id):
    """Update report status (REVIEWING, RESOLVED, DISMISSED)."""
    report = ReportModel.get_by_id(report_id)
    if not report:
        return error_response(code='NOT_FOUND', message='Report not found.', status_code=404)

    data = request.get_json()
    new_status = str(data.get('status', '')).upper().strip()
    if new_status not in ReportModel.STATUSES:
        return error_response(code='INVALID_STATUS', message=f"Status must be one of: {', '.join(ReportModel.STATUSES)}.", status_code=400)

    if not ReportModel.is_valid_transition(report['status'], new_status):
        return error_response(
            code='INVALID_TRANSITION',
            message=f"Cannot transition report from {report['status']} to {new_status}.",
            status_code=400,
        )

    success = ReportModel.update_status(report_id, new_status, admin_id=g.user_id)
    if not success:
        return error_response(code='DATABASE_ERROR', message='Failed to update report status.', status_code=500)

    return success_response(message=f'Report status updated to {new_status}.')


# ===========================================================================
# 4. CATEGORY ADMINISTRATION
# ===========================================================================

@admin_bp.route('/categories', methods=['GET'])
@jwt_required
@role_required('admin')
def get_admin_categories():
    """List all categories including inactive ones."""
    categories = CategoryModel.get_all()
    return success_response(data={'items': categories})


@admin_bp.route('/categories', methods=['POST'])
@jwt_required
@role_required('admin')
@validate_json(required_fields=['name', 'slug'])
def create_category():
    """Create a new product category."""
    data = request.get_json()
    name = str(data.get('name', '')).strip()
    slug = str(data.get('slug', '')).lower().strip()
    description = str(data.get('description', '')).strip()
    icon = str(data.get('icon', '')).strip()

    if not name or len(name) > 50:
        return error_response(code='INVALID_NAME', message='Name must be between 1 and 50 characters.', status_code=400)

    if not slug or len(slug) > 50:
        return error_response(code='INVALID_SLUG', message='Slug must be between 1 and 50 characters.', status_code=400)

    cat_id = CategoryModel.create_category(name=name, slug=slug, description=description, icon=icon)
    if not cat_id:
        return error_response(code='DUPLICATE_CATEGORY', message='A category with this slug already exists.', status_code=409)

    return success_response(data={'category_id': cat_id, 'message': 'Category created successfully.'}, status_code=201)


@admin_bp.route('/categories/<slug>', methods=['PATCH'])
@jwt_required
@role_required('admin')
def update_category(slug):
    """Update fields of an existing category by slug."""
    cat = CategoryModel.get_by_slug(slug)
    if not cat:
        return error_response(code='NOT_FOUND', message='Category not found.', status_code=404)

    data = request.get_json() or {}
    updates = {}

    if 'name' in data:
        name = str(data['name']).strip()
        if not name or len(name) > 50:
            return error_response(code='INVALID_NAME', message='Name must be between 1 and 50 characters.', status_code=400)
        updates['name'] = name

    if 'description' in data:
        updates['description'] = str(data['description']).strip()

    if 'icon' in data:
        updates['icon'] = str(data['icon']).strip()

    if 'is_active' in data:
        if not isinstance(data['is_active'], bool):
            return error_response(code='INVALID_INPUT', message='is_active must be a boolean.', status_code=400)
        updates['is_active'] = data['is_active']

    if not updates:
        return success_response(message='No fields to update.')

    success = CategoryModel.update_category(slug, updates)
    if not success:
        return error_response(code='DATABASE_ERROR', message='Failed to update category.', status_code=500)

    return success_response(message='Category updated successfully.')


# ===========================================================================
# 5. MARKETPLACE ANALYTICS OVERVIEW
# ===========================================================================

@admin_bp.route('/analytics/overview', methods=['GET'])
@jwt_required
@role_required('admin')
def get_analytics_overview():
    """
    Returns aggregated marketplace analytics overview using MongoDB count/aggregation queries.
    """
    try:
        users_col = UserModel.collection()
        products_col = ProductModel.collection()
        transactions_col = TransactionModel.collection()
        requests_col = PurchaseRequestModel.collection()
        reviews_col = ReviewModel.collection()
        categories_col = CategoryModel.collection()

        # User Metrics
        total_users = users_col.count_documents({})
        active_users = users_col.count_documents({'account_status': 'ACTIVE'})
        suspended_users = users_col.count_documents({'account_status': 'SUSPENDED'})
        student_users = users_col.count_documents({'role': 'student'})
        admin_users = users_col.count_documents({'role': 'admin'})

        # Listing Metrics
        total_products = products_col.count_documents({})
        active_products = products_col.count_documents({'status': 'ACTIVE'})
        reserved_products = products_col.count_documents({'status': 'RESERVED'})
        sold_products = products_col.count_documents({'status': 'SOLD'})
        removed_products = products_col.count_documents({'status': 'REMOVED'})

        # Transaction Metrics
        total_transactions = transactions_col.count_documents({})
        pending_transactions = transactions_col.count_documents({'status': 'PENDING'})
        reserved_transactions = transactions_col.count_documents({'status': 'RESERVED'})
        completed_transactions = transactions_col.count_documents({'status': 'COMPLETED'})
        cancelled_transactions = transactions_col.count_documents({'status': 'CANCELLED'})

        # Purchase Request Metrics
        total_requests = requests_col.count_documents({})
        pending_requests = requests_col.count_documents({'status': 'PENDING'})
        accepted_requests = requests_col.count_documents({'status': 'ACCEPTED'})
        rejected_requests = requests_col.count_documents({'status': 'REJECTED'})
        cancelled_requests = requests_col.count_documents({'status': 'CANCELLED'})

        # Review Metrics & Avg Rating Aggregation
        total_reviews = reviews_col.count_documents({})
        avg_rating = 0.0
        if total_reviews > 0:
            rating_agg = list(reviews_col.aggregate([
                {'$group': {'_id': None, 'avg_rating': {'$avg': '$rating'}}}
            ]))
            if rating_agg and 'avg_rating' in rating_agg[0]:
                avg_rating = round(float(rating_agg[0]['avg_rating']), 2)

        # Report Metrics
        reports_col = ReportModel.collection()
        total_reports = reports_col.count_documents({})
        open_reports = reports_col.count_documents({'status': 'OPEN'})

        # Category Breakdown Aggregation
        cat_agg = list(products_col.aggregate([
            {'$group': {'_id': '$category_id', 'product_count': {'$sum': 1}}},
            {'$sort': {'product_count': -1}}
        ]))
        category_metrics = []
        for c in cat_agg:
            cat_slug = c['_id']
            if cat_slug:
                cat_doc = categories_col.find_one({'slug': cat_slug})
                cat_name = cat_doc['name'] if cat_doc else cat_slug
                category_metrics.append({
                    'category_id': cat_slug,
                    'name': cat_name,
                    'product_count': c['product_count']
                })

        return success_response(data={
            'users': {
                'total': total_users,
                'active': active_users,
                'suspended': suspended_users,
                'students': student_users,
                'admins': admin_users
            },
            'products': {
                'total': total_products,
                'active': active_products,
                'reserved': reserved_products,
                'sold': sold_products,
                'removed': removed_products
            },
            'transactions': {
                'total': total_transactions,
                'pending': pending_transactions,
                'reserved': reserved_transactions,
                'completed': completed_transactions,
                'cancelled': cancelled_transactions
            },
            'purchase_requests': {
                'total': total_requests,
                'pending': pending_requests,
                'accepted': accepted_requests,
                'rejected': rejected_requests,
                'cancelled': cancelled_requests
            },
            'reviews': {
                'total': total_reviews,
                'average_rating': avg_rating
            },
            'reports': {
                'total': total_reports,
                'open': open_reports
            },
            'categories': category_metrics
        })
    except Exception as e:
        return error_response(code='DATABASE_ERROR', message='Failed to calculate analytics.', status_code=500)
