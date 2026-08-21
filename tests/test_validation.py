import json
from flask import Flask, jsonify
import pytest
from backend.validation import validate_json
from backend.responses import success_response
from backend.errors import register_error_handlers

@pytest.fixture
def validation_app():
    app = Flask(__name__)
    register_error_handlers(app)
    
    @app.route('/test-val', methods=['POST'])
    @validate_json(required_fields=['name', 'age'], expected_types={'age': int})
    def test_val_route():
        return success_response(data="valid")
        
    return app

@pytest.fixture
def val_client(validation_app):
    return validation_app.test_client()

def test_validation_not_json(val_client):
    response = val_client.post('/test-val', data="not-json")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error']['code'] == 'INVALID_REQUEST'

def test_validation_missing_field(val_client):
    response = val_client.post('/test-val', json={"name": "Alice"})
    assert response.status_code == 422
    data = json.loads(response.data)
    assert data['error']['code'] == 'MISSING_FIELD'

def test_validation_invalid_type(val_client):
    response = val_client.post('/test-val', json={"name": "Alice", "age": "thirty"})
    assert response.status_code == 422
    data = json.loads(response.data)
    assert data['error']['code'] == 'INVALID_TYPE'

def test_validation_success(val_client):
    response = val_client.post('/test-val', json={"name": "Alice", "age": 30})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
