from flask import Blueprint, jsonify, current_app

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'application': 'SecondSpin',
        'environment': current_app.config.get('FLASK_ENV', 'unknown'),
        'version': '1.0.0'
    }), 200
