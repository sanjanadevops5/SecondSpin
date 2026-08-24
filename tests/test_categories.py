import pytest
from backend.models.category import CategoryModel

def test_get_categories(client, app, monkeypatch):
    # Mock database call
    mock_categories = [
        {'_id': '1', 'name': 'Textbooks', 'slug': 'textbooks', 'is_active': True},
        {'_id': '2', 'name': 'Electronics', 'slug': 'electronics', 'is_active': True}
    ]
    
    # We must mock CategoryModel.get_all_active since it uses the database
    monkeypatch.setattr(CategoryModel, "get_all_active", lambda: mock_categories)
    
    response = client.get('/api/v1/categories/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data['data']) == 2
    assert data['data'][0]['name'] == 'Textbooks'
