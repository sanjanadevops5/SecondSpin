from functools import wraps
from flask import request
from .responses import error_response

def validate_json(required_fields=None, expected_types=None):
    """
    A foundation decorator to validate incoming JSON requests.
    
    :param required_fields: list of strings, keys that must exist in the JSON.
    :param expected_types: dict mapping keys to Python types for basic validation.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return error_response(
                    code="INVALID_REQUEST",
                    message="Request payload must be JSON",
                    status_code=400
                )
            
            data = request.get_json()
            
            if required_fields:
                for field in required_fields:
                    if field not in data:
                        return error_response(
                            code="MISSING_FIELD",
                            message=f"Missing required field: '{field}'",
                            status_code=422
                        )
            
            if expected_types:
                for field, expected_type in expected_types.items():
                    if field in data and not isinstance(data[field], expected_type):
                        return error_response(
                            code="INVALID_TYPE",
                            message=f"Field '{field}' must be of type {expected_type.__name__}",
                            status_code=422
                        )
                        
            return f(*args, **kwargs)
        return decorated_function
    return decorator
