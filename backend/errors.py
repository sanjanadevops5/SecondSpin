import logging
from .responses import error_response


def register_error_handlers(app):
    """Register application-wide error handlers."""
    
    # Catch any generic exception
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the full exception for debugging internally
        logging.exception("Unhandled exception occurred")
        # Return generic JSON error
        return error_response(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred on the server.",
            status_code=500
        )

    @app.errorhandler(400)
    def bad_request(error):
        return error_response(code="BAD_REQUEST", message=str(error.description if hasattr(error, 'description') else error), status_code=400)

    @app.errorhandler(401)
    def unauthorized(error):
        return error_response(code="UNAUTHORIZED", message="Authentication is required to access this resource.", status_code=401)

    @app.errorhandler(403)
    def forbidden(error):
        return error_response(code="FORBIDDEN", message="You do not have permission to access this resource.", status_code=403)

    @app.errorhandler(404)
    def not_found(error):
        return error_response(code="NOT_FOUND", message="The requested resource was not found.", status_code=404)

    @app.errorhandler(409)
    def conflict(error):
        return error_response(code="CONFLICT", message=str(error.description if hasattr(error, 'description') else error), status_code=409)

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return error_response(code="UNPROCESSABLE_ENTITY", message=str(error.description if hasattr(error, 'description') else error), status_code=422)

    @app.errorhandler(500)
    def internal_server_error(error):
        return error_response(code="INTERNAL_SERVER_ERROR", message="An unexpected error occurred.", status_code=500)
