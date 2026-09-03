import json
import pytest

@pytest.fixture
def auth_token(client):
    register_data = {
        "name": "User Profile Test",
        "email": "profile@college.edu",
        "password": "password123"
    }
    client.post('/api/v1/auth/register', json=register_data)
    res = client.post('/api/v1/auth/login', json={
        "email": register_data['email'],
        "password": register_data['password']
    })
    return json.loads(res.data)['data']['token']

def test_get_me(client, auth_token):
    res = client.get('/api/v1/users/me', headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data['success'] is True
    assert data['data']['user']['name'] == "User Profile Test"
    assert data['data']['user']['email'] == "profile@college.edu"

def test_update_me(client, auth_token):
    res = client.put('/api/v1/users/me', 
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"department": "Computer Science"}
    )
    assert res.status_code == 200
    
    res2 = client.get('/api/v1/users/me', headers={"Authorization": f"Bearer {auth_token}"})
    data = json.loads(res2.data)
    assert data['data']['user']['department'] == "Computer Science"

def test_update_me_restricted_field(client, auth_token):
    res = client.put('/api/v1/users/me', 
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"role": "admin"}
    )
    assert res.status_code == 403
