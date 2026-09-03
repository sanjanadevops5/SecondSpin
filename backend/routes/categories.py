from flask import Blueprint, request
from backend.responses import success_response, error_response
from backend.models.category import CategoryModel
from backend.services.smart_service import get_popular_categories

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/', methods=['GET'])
def get_categories():
    try:
        categories = CategoryModel.get_all_active()
        return success_response(data=categories)
    except Exception as e:
        return error_response(code="DATABASE_ERROR", message="Failed to fetch categories.", status_code=500)

@categories_bp.route('/popular', methods=['GET'])
def get_popular_categories_route():
    try:
        limit = int(request.args.get('limit', 10))
        if limit < 1: limit = 10
        if limit > 50: limit = 50
    except ValueError:
        return error_response(code="INVALID_LIMIT", message="Limit must be a positive integer.", status_code=400)

    try:
        items = get_popular_categories(limit=limit)
        return success_response(data={'items': items, 'count': len(items)})
    except Exception as e:
        return error_response(code="DATABASE_ERROR", message="Failed to fetch popular categories.", status_code=500)
