from flask import jsonify

def success_response(data=None, message="Request successful", status_code=200):
    """
    Standardize a successful JSON response.
    """
    response_body = {
        "success": True,
        "message": message
    }
    if data is not None:
        response_body["data"] = data
        
    return jsonify(response_body), status_code

def error_response(code, message, status_code=400):
    """
    Standardize an error JSON response.
    """
    response_body = {
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }
    return jsonify(response_body), status_code
