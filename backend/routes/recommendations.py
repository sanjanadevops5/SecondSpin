"""
Recommendations Blueprint — Phase 9
Provides personalized recommendations for authenticated users based on their interaction history,
with seamless cold-start fallback to campus-wide popular items.
"""
from flask import Blueprint, request, g
from backend.responses import success_response, error_response
from backend.auth_middleware import jwt_required
from backend.services.smart_service import get_personalized_recommendations

recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('', methods=['GET'], strict_slashes=False)
@recommendations_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required
def get_user_recommendations():
    """
    Returns personalized product recommendations for the authenticated user.
    User identity is derived strictly from the authenticated JWT (g.user_id).
    """
    try:
        limit = int(request.args.get('limit', 10))
        if limit < 1: limit = 10
        if limit > 50: limit = 50
    except ValueError:
        return error_response(code='INVALID_LIMIT', message='Limit must be a positive integer.', status_code=400)

    try:
        items = get_personalized_recommendations(g.user_id, limit=limit)
        return success_response(data={'items': items, 'count': len(items)})
    except Exception as e:
        return error_response(code='DATABASE_ERROR', message='Failed to generate recommendations.', status_code=500)
