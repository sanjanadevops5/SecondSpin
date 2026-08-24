import json
from flask import Blueprint, jsonify
from backend.auth_middleware import jwt_required, role_required

test_bp = Blueprint('test', __name__)

@test_bp.route('/protected')
@jwt_required
def protected_route():
    return jsonify({"success": True})

@test_bp.route('/admin')
@jwt_required
@role_required('admin')
def admin_route():
    return jsonify({"success": True})

def test_unauthorized_missing_token(client):
    client.application.register_blueprint(test_bp, url_prefix='/test')
    res = client.get('/test/protected')
    assert res.status_code == 401

def test_unauthorized_invalid_token(client):
    client.application.register_blueprint(test_bp, url_prefix='/test')
    res = client.get('/test/protected', headers={"Authorization": "Bearer invalidtoken123"})
    assert res.status_code == 401

def test_role_required_forbidden(client):
    client.application.register_blueprint(test_bp, url_prefix='/test')
    
    # Register and login as student
    client.post('/api/v1/auth/register', json={
        "name": "Student",
        "email": "student@college.edu",
        "password": "password123"
    })
    res_login = client.post('/api/v1/auth/login', json={
        "email": "student@college.edu",
        "password": "password123"
    })
    token = json.loads(res_login.data)['data']['token']
    
    res = client.get('/test/admin', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
