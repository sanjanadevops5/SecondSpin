import json
import pytest

@pytest.fixture
def register_data():
    return {
        "name": "Test User",
        "email": "test@student.college.edu",
        "password": "password123"
    }

def test_register_success(client, register_data):
    res = client.post('/api/v1/auth/register', json=register_data)
    assert res.status_code == 201
    data = json.loads(res.data)
    assert data['success'] is True
    assert 'user_id' in data['data']

def test_register_missing_fields(client):
    res = client.post('/api/v1/auth/register', json={"name": "Test"})
    assert res.status_code == 422

def test_register_invalid_email(client, register_data):
    register_data['email'] = "invalid_email"
    res = client.post('/api/v1/auth/register', json=register_data)
    assert res.status_code == 400

def test_register_duplicate_email(client, register_data):
    client.post('/api/v1/auth/register', json=register_data)
    res = client.post('/api/v1/auth/register', json=register_data)
    assert res.status_code == 409

def test_login_success(client, register_data):
    client.post('/api/v1/auth/register', json=register_data)
    res = client.post('/api/v1/auth/login', json={
        "email": register_data['email'],
        "password": register_data['password']
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data['success'] is True
    assert 'token' in data['data']
    assert 'password_hash' not in data['data']['user']
    assert data['data']['user']['verification_status'] == 'VERIFIED'

def test_login_invalid_password(client, register_data):
    client.post('/api/v1/auth/register', json=register_data)
    res = client.post('/api/v1/auth/login', json={
        "email": register_data['email'],
        "password": "wrongpassword"
    })
    assert res.status_code == 401

def test_login_unknown_email(client):
    res = client.post('/api/v1/auth/login', json={
        "email": "unknown@example.com",
        "password": "password123"
    })
    assert res.status_code == 401
