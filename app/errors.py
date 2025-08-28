from flask import jsonify

def register_error_handlers(app):

    #error handlers 400, 404, 500
    @app.errorhandler(400)
    def bad_request_error(error):
        response = jsonify({"error": "Bad request"})
        response.status_code = 400
        return response

    @app.errorhandler(404)
    def not_found_error(error):
        response = jsonify({"error": "Resource not found"})
        response.status_code = 404
        return response

    @app.errorhandler(500)
    def internal_error(error):
        response = jsonify({"error": "Internal server error"})
        response.status_code = 500
        return response
    
    # Manejo de errores de validación de Marshmallow
    from marshmallow import ValidationError

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        response = jsonify({"error": "Validation error", "messages": error.messages})
        response.status_code = 400
        return response