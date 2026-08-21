import json


def test_health_endpoint(client):
    """Test the /api/v1/health endpoint returns correct JSON and 200 OK."""
    response = client.get('/api/v1/health')

    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['success'] is True
    assert data['message'] == "Request successful"
    
    payload = data['data']
    assert payload['status'] == 'healthy'
    assert payload['application'] == 'SecondSpin'
    assert payload['environment'] == 'testing'
    assert payload['api_version'] == 'v1'
