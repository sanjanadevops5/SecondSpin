import json

def test_404_error(client):
    """Test that a non-existent route returns the standard 404 JSON error."""
    response = client.get('/api/v1/does_not_exist')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'error' in data
    assert data['error']['code'] == 'NOT_FOUND'
