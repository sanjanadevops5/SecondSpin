import json

def test_health_endpoint(client):
    """Test the /api/health endpoint returns correct JSON and 200 OK."""
    response = client.get('/api/health')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['application'] == 'SecondSpin'
    assert data['environment'] == 'testing'
    assert 'version' in data
