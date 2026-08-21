from flask import current_app
from . import api_v1_bp
from backend.responses import success_response

@api_v1_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    return success_response(
        data={
            'application': 'SecondSpin',
            'status': 'healthy',
            'environment': current_app.config.get('FLASK_ENV', 'unknown'),
            'api_version': 'v1'
        }
    )
