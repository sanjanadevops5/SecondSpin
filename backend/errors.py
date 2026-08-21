from flask import jsonify

def register_error_handlers(app):
    """Register application-wide error handlers."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad Request', 'message': str(error)}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized', 'message': str(error)}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden', 'message': str(error)}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not Found', 'message': str(error)}), 404

    @app.errorhandler(409)
    def conflict(error):
        return jsonify({'error': 'Conflict', 'message': str(error)}), 409

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({'error': 'Unprocessable Entity', 'message': str(error)}), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({'error': 'Internal Server Error', 'message': 'An unexpected error occurred.'}), 500
