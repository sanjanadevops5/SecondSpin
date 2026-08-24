import datetime
import jwt
from flask import Blueprint, request, current_app
from backend.responses import success_response, error_response
from backend.validation import validate_json
from backend.models.user import UserModel
import re

auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['POST'])
@validate_json(required_fields=['name', 'email', 'password'])
def register():
    data = request.get_json()
    name = data['name'].strip()
    email = data['email'].strip()
    password = data['password']
    
    if not name:
        return error_response(code="INVALID_INPUT", message="Name cannot be empty.", status_code=400)
        
    if not is_valid_email(email):
        return error_response(code="INVALID_EMAIL", message="Invalid email format.", status_code=400)
        
    if len(password) < 8:
        return error_response(code="WEAK_PASSWORD", message="Password must be at least 8 characters long.", status_code=400)
        
    allowed_domains = current_app.config.get('ALLOWED_EMAIL_DOMAINS', [])
    
    user_id = UserModel.create_user(name, email, password, allowed_domains)
    
    if not user_id:
        return error_response(code="EMAIL_EXISTS", message="Email is already registered.", status_code=409)
        
    return success_response(
        data={"user_id": user_id, "message": "Registration successful."},
        status_code=201
    )

@auth_bp.route('/login', methods=['POST'])
@validate_json(required_fields=['email', 'password'])
def login():
    data = request.get_json()
    email = data['email'].strip()
    password = data['password']
    
    user = UserModel.get_by_email(email)
    
    # Generic error message to prevent user enumeration
    invalid_auth_msg = "Invalid email or password."
    
    if not user or not UserModel.verify_password(user['password_hash'], password):
        return error_response(code="INVALID_CREDENTIALS", message=invalid_auth_msg, status_code=401)
        
    if user.get('account_status') != 'ACTIVE':
        return error_response(code="FORBIDDEN", message=f"Account is {user.get('account_status', 'inactive')}.", status_code=403)
        
    # Generate JWT
    secret = current_app.config.get('JWT_SECRET_KEY')
    expires_in = current_app.config.get('JWT_EXPIRES_IN', 86400)
    
    token = jwt.encode({
        'sub': str(user['_id']),
        'role': user.get('role', 'student'),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in),
        'iat': datetime.datetime.utcnow()
    }, secret, algorithm="HS256")
    
    # Return token but NEVER password_hash
    user_data = {
        'id': str(user['_id']),
        'name': user.get('name'),
        'email': user.get('email'),
        'role': user.get('role'),
        'verification_status': user.get('verification_status')
    }
    
    return success_response(data={
        "token": token,
        "user": user_data
    })
