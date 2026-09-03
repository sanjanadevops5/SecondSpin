from flask import Blueprint, request, g
from backend.responses import success_response, error_response
from backend.auth_middleware import jwt_required
from backend.models.user import UserModel
from backend.validation import validate_json

users_bp = Blueprint('users', __name__)

@users_bp.route('/me', methods=['GET'])
@jwt_required
def get_me():
    user = UserModel.get_by_id(g.user_id)
    if not user:
        return error_response(code="NOT_FOUND", message="User not found.", status_code=404)
        
    user_data = {
        '_id': str(user['_id']),
        'name': user.get('name'),
        'email': user.get('email'),
        'role': user.get('role'),
        'department': user.get('department'),
        'verification_status': user.get('verification_status'),
        'account_status': user.get('account_status'),
        'profile': user.get('profile', {})
    }
    
    return success_response(data={'user': user_data})

@users_bp.route('/me', methods=['PUT'])
@jwt_required
def update_me():
    data = request.get_json() or {}
    
    # Only allow safe fields to be updated
    allowed_fields = ['name', 'department', 'profile']
    updates = {}
    
    for field in allowed_fields:
        if field in data:
            updates[field] = data[field]
            
    # Protect against trying to update role or status
    restricted_fields = ['role', 'verification_status', 'account_status', 'email', 'password_hash']
    for field in restricted_fields:
        if field in data:
            return error_response(code="FORBIDDEN", message=f"Cannot update restricted field: {field}", status_code=403)
            
    if not updates:
        return success_response(message="No valid fields to update.")
        
    success = UserModel.update_profile(g.user_id, updates)
    if not success:
        return error_response(code="UPDATE_FAILED", message="Failed to update profile.", status_code=500)
        
    return success_response(message="Profile updated successfully.")
