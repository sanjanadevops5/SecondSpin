from flask import Blueprint
from backend.responses import success_response, error_response
from backend.models.category import CategoryModel

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/', methods=['GET'])
def get_categories():
    try:
        categories = CategoryModel.get_all_active()
        return success_response(data=categories)
    except Exception as e:
        return error_response(code="DATABASE_ERROR", message="Failed to fetch categories.", status_code=500)
