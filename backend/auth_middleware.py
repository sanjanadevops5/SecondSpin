from functools import wraps
import jwt
from flask import request, current_app, g
from backend.responses import error_response
from backend.models.user import UserModel

def jwt_required(f):
    """
    Decorator to protect routes with JWT authentication.
    Injects user ID and role into flask's global 'g' object.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
            
        if not token:
            return error_response(code="UNAUTHORIZED", message="Authentication token is missing.", status_code=401)
            
        try:
            secret = current_app.config.get('JWT_SECRET_KEY')
            data = jwt.decode(token, secret, algorithms=["HS256"])
            
            # Fetch user to ensure they still exist and are active
            user = UserModel.get_by_id(data['sub'])
            if not user:
                return error_response(code="UNAUTHORIZED", message="User no longer exists.", status_code=401)
                
            if user.get('account_status') != 'ACTIVE':
                return error_response(code="FORBIDDEN", message=f"Account is {user.get('account_status', 'inactive')}.", status_code=403)
                
            g.user_id = str(user['_id'])
            g.user_role = user.get('role', 'student')
            
        except jwt.ExpiredSignatureError:
            return error_response(code="UNAUTHORIZED", message="Token has expired.", status_code=401)
        except jwt.InvalidTokenError:
            return error_response(code="UNAUTHORIZED", message="Invalid token.", status_code=401)
            
        return f(*args, **kwargs)
        
    return decorated


def role_required(required_role):
    """
    Decorator to protect routes by user role.
    Must be used AFTER @jwt_required.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user_role'):
                return error_response(code="INTERNAL_SERVER_ERROR", message="Role check failed.", status_code=500)
                
            if g.user_role != required_role:
                return error_response(code="FORBIDDEN", message=f"Requires {required_role} privileges.", status_code=403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
