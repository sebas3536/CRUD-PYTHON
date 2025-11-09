"""
Módulo de gestión centralizada de errores HTTP para la API REST.

Este módulo implementa un sistema de manejo de errores estandarizado que proporciona
respuestas JSON consistentes y estructuradas para todos los tipos de errores. Sigue
las mejores prácticas de REST API y el estándar RFC 9457 para detalles de problemas.

El módulo maneja:
    - Errores HTTP estándar (400, 404, 500, etc.)
    - Errores de validación de Marshmallow (422)
    - Errores de integridad de base de datos (409)
    - Excepciones personalizadas de la API
    - Errores no previstos con logging apropiado

Todas las respuestas siguen un formato uniforme que incluye tipo de error,
mensaje descriptivo y detalles opcionales para facilitar el debugging.

Example:
    Registrar manejadores en la aplicación::

        from app.errors import register_error_handlers
        
        app = Flask(__name__)
        register_error_handlers(app)

References:
    - Flask Error Handling: https://flask.palletsprojects.com/errorhandling/
    - RFC 9457 Problem Details: https://www.rfc-editor.org/rfc/rfc9457.html
"""

from flask import jsonify, current_app
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException


class APIError(Exception):
    """
    Excepción personalizada para errores específicos de la API.
    
    Permite lanzar errores personalizados con código de estado HTTP,
    mensaje descriptivo y detalles adicionales opcionales. Esta clase
    proporciona un mecanismo consistente para manejar errores de negocio
    y validaciones específicas de la aplicación.
    
    Attributes:
        message (str): Mensaje descriptivo del error para el cliente.
        status_code (int): Código de estado HTTP apropiado (default: 400).
        details (dict): Información adicional sobre el error, como campos
            afectados o valores inválidos.
    
    Example:
        Lanzar un error personalizado::
        
            if not user.is_active:
                raise APIError(
                    message="Usuario inactivo",
                    status_code=403,
                    details={"user_id": user.id, "status": "inactive"}
                )
    
    Note:
        Los errores APIError son capturados automáticamente por el
        error handler registrado y convertidos en respuestas JSON.
    """
    
    def __init__(self, message, status_code=400, details=None):
        """
        Inicializa una nueva excepción APIError.
        
        Args:
            message (str): Mensaje descriptivo del error.
            status_code (int, optional): Código HTTP del error. Default 400.
            details (dict, optional): Información adicional del error.
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


def register_error_handlers(app):
    """
    Registra manejadores de errores globales en la aplicación Flask.
    
    Configura error handlers para todos los tipos de errores comunes,
    asegurando respuestas JSON consistentes y estructuradas. Los manejadores
    capturan tanto errores HTTP estándar como excepciones específicas de
    frameworks (Marshmallow, SQLAlchemy) y de la aplicación.
    
    Args:
        app (Flask): Instancia de la aplicación Flask donde se registrarán
            los manejadores de errores.
    
    Note:
        - Los errores se registran en el logger antes de enviar la respuesta
        - Las transacciones de base de datos se revierten en errores de integridad
        - El formato de respuesta sigue el estándar de Problem Details
    
    Error Handlers Registrados:
        - 400 Bad Request: Solicitudes mal formadas o con datos inválidos
        - 404 Not Found: Recursos no encontrados
        - 500 Internal Server Error: Errores internos del servidor
        - 422 Unprocessable Entity: Errores de validación de Marshmallow
        - 409 Conflict: Violaciones de integridad de base de datos
        - APIError: Errores personalizados de la aplicación
        - Exception: Fallback para cualquier error no manejado
    
    Example:
        Uso típico en application factory::
        
            def create_app():
                app = Flask(__name__)
                register_error_handlers(app)
                return app
    
    See Also:
        - _create_error_response(): Formato estándar de respuestas de error
        - APIError: Clase para excepciones personalizadas
    """
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """
        Maneja errores de solicitud inválida (400 Bad Request).
        
        Se activa cuando el cliente envía datos mal formados, parámetros
        inválidos o una solicitud que no puede ser procesada por razones
        sintácticas.
        
        Args:
            error: Objeto de error capturado por Flask.
        
        Returns:
            tuple: Respuesta JSON con detalles del error y código 400.
        
        Example:
            Este handler se activa automáticamente::
            
                # Cliente envía JSON inválido
                POST /clientes
                Body: {invalid json}
                
                # Respuesta
                {
                    "success": false,
                    "error": {
                        "type": "BAD_REQUEST",
                        "message": "La solicitud contiene datos inválidos..."
                    }
                }
        """
        return _create_error_response(
            status_code=400,
            error_type="BAD_REQUEST",
            message="La solicitud contiene datos inválidos o mal formados."
        )
    
    @app.errorhandler(404)
    def not_found_error(error):
        """
        Maneja errores cuando el recurso solicitado no existe (404 Not Found).
        
        Se activa cuando se intenta acceder a un endpoint inexistente o
        cuando un recurso específico (por ID) no se encuentra en la base
        de datos.
        
        Args:
            error: Objeto de error capturado por Flask.
        
        Returns:
            tuple: Respuesta JSON con detalles del error y código 404.
        
        Example:
            GET /clientes/999 (ID inexistente)
            
            Response:
            {
                "success": false,
                "error": {
                    "type": "NOT_FOUND",
                    "message": "El recurso solicitado no existe."
                }
            }
        """
        return _create_error_response(
            status_code=404,
            error_type="NOT_FOUND",
            message="El recurso solicitado no existe."
        )
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """
        Maneja errores internos del servidor (500 Internal Server Error).
        
        Captura errores no manejados que ocurren durante el procesamiento
        de la solicitud. El error completo se registra en el log con stack
        trace para facilitar el debugging.
        
        Args:
            error: Objeto de error capturado por Flask.
        
        Returns:
            tuple: Respuesta JSON genérica y código 500.
        
        Warning:
            No exponer detalles del error al cliente en producción por
            razones de seguridad. Los detalles completos están en los logs.
        
        Note:
            Este handler registra el error completo con exc_info para
            incluir el stack trace en los logs del servidor.
        """
        current_app.logger.error(f"Error interno del servidor: {error}")
        return _create_error_response(
            status_code=500,
            error_type="INTERNAL_SERVER_ERROR",
            message="Ocurrió un error interno en el servidor. Por favor, intente más tarde."
        )
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """
        Maneja errores de validación de esquemas Marshmallow (422).
        
        Captura ValidationError de Marshmallow cuando los datos no cumplen
        con las reglas de validación definidas en los schemas. Los detalles
        incluyen qué campos fallaron y por qué razón.
        
        Args:
            error (ValidationError): Excepción de Marshmallow con mensajes
                de validación estructurados por campo.
        
        Returns:
            tuple: Respuesta JSON con detalles de validación y código 422.
        
        Example:
            POST /clientes con email inválido::
            
                Body: {"nombre": "Juan", "email": "invalid"}
                
                Response:
                {
                    "success": false,
                    "error": {
                        "type": "VALIDATION_ERROR",
                        "message": "Los datos no cumplen requisitos...",
                        "details": {
                            "email": ["Not a valid email address."]
                        }
                    }
                }
        
        Note:
            El código 422 (Unprocessable Entity) es el estándar REST para
            errores de validación semántica, diferenciándose del 400 que
            indica errores sintácticos.
        """
        return _create_error_response(
            status_code=422,
            error_type="VALIDATION_ERROR",
            message="Los datos proporcionados no cumplen con los requisitos de validación.",
            details=error.messages
        )
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        """
        Maneja errores de integridad de base de datos (409 Conflict).
        
        Captura violaciones de restricciones de base de datos como claves
        únicas, claves foráneas o restricciones CHECK. Realiza rollback
        automático de la transacción para mantener consistencia.
        
        Args:
            error (IntegrityError): Excepción de SQLAlchemy con detalles
                de la violación de integridad.
        
        Returns:
            tuple: Respuesta JSON con mensaje genérico y código 409.
        
        Warning:
            El mensaje de error de base de datos completo se registra en
            logs pero NO se expone al cliente para evitar filtraciones de
            información de la estructura de la base de datos.
        
        Note:
            - Se realiza rollback automático de la sesión de base de datos
            - Común en casos de emails duplicados, IDs ya existentes, etc.
        
        Example:
            Intentar crear cliente con email duplicado::
            
                POST /clientes
                Body: {"email": "existente@example.com", ...}
                
                Response: 409 Conflict
                {
                    "success": false,
                    "error": {
                        "type": "INTEGRITY_ERROR",
                        "message": "Violan restricciones de BD..."
                    }
                }
        """
        current_app.logger.error(f"Error de integridad de BD: {error}")
        db_session = None
        try:
            from . import db
            db.session.rollback()
        except Exception:
            pass
        
        return _create_error_response(
            status_code=409,
            error_type="INTEGRITY_ERROR",
            message="Los datos violan restricciones de la base de datos (ej: email duplicado)."
        )
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """
        Maneja excepciones personalizadas de la API (APIError).
        
        Procesa errores específicos del dominio de negocio lanzados
        explícitamente en la lógica de la aplicación usando la clase
        APIError personalizada.
        
        Args:
            error (APIError): Instancia de la excepción personalizada con
                mensaje, código de estado y detalles opcionales.
        
        Returns:
            tuple: Respuesta JSON con información del error personalizado
                y el código de estado especificado en la excepción.
        
        Example:
            En el código de la aplicación::
            
                if not cliente.activo:
                    raise APIError(
                        message="Cliente desactivado",
                        status_code=403,
                        details={"cliente_id": cliente.id}
                    )
                
                # Se convierte automáticamente en respuesta JSON
        """
        return _create_error_response(
            status_code=error.status_code,
            error_type="API_ERROR",
            message=error.message,
            details=error.details
        )
    
    @app.errorhandler(Exception)
    def handle_generic_error(error):
        """
        Maneja excepciones genéricas no previstas (fallback handler).
        
        Actúa como red de seguridad para capturar cualquier excepción no
        manejada por handlers específicos. Registra el error completo con
        stack trace y devuelve respuesta genérica al cliente.
        
        Args:
            error (Exception): Cualquier excepción de Python no manejada
                por otros error handlers.
        
        Returns:
            tuple: Respuesta JSON genérica y código 500.
        
        Warning:
            Este handler indica un error no previsto en la aplicación.
            Revisar los logs y considerar agregar un handler específico
            si el error es recurrente.
        
        Note:
            - Se registra con exc_info=True para capturar stack trace completo
            - Último recurso: previene exponer tracebacks de Python al cliente
            - Señal de que puede necesitarse un handler más específico
        """
        current_app.logger.error(f"Error no controlado: {error}", exc_info=True)
        return _create_error_response(
            status_code=500,
            error_type="INTERNAL_SERVER_ERROR",
            message="Error inesperado en el servidor."
        )


def _create_error_response(status_code, error_type, message, details=None):
    """
    Crea una respuesta de error estandarizada en formato JSON.
    
    Genera respuestas consistentes siguiendo un formato estructurado que
    facilita el parsing y manejo de errores por parte de los clientes de
    la API. El formato sigue el estándar de Problem Details para APIs REST.
    
    Args:
        status_code (int): Código de estado HTTP (400, 404, 500, etc.).
        error_type (str): Identificador del tipo de error en mayúsculas.
            Útil para manejo programático por el cliente.
        message (str): Mensaje descriptivo legible por humanos que explica
            el error y posibles soluciones.
        details (dict, optional): Información adicional estructurada sobre
            el error, como campos afectados o valores inválidos.
    
    Returns:
        tuple: Tupla de (Response object, status_code) lista para ser
            retornada desde un view handler de Flask.
    
    Response Format:
        {
            "success": false,
            "error": {
                "type": "ERROR_TYPE",
                "message": "Descripción legible del error",
                "details": {...}  // Opcional
            }
        }
    
    Example:
        Crear respuesta de error manualmente::
        
            return _create_error_response(
                status_code=422,
                error_type="VALIDATION_ERROR",
                message="Email inválido",
                details={"field": "email", "value": "invalid"}
            )
    
    Note:
        - El campo 'success' facilita el parsing en clientes
        - 'error_type' permite switch statements en cliente para manejo específico
        - 'details' solo se incluye si tiene contenido (no null/empty dict)
    
    See Also:
        - RFC 9457 Problem Details for HTTP APIs
        - REST API Error Handling Best Practices
    """
    response_data = {
        "success": False,
        "error": {
            "type": error_type,
            "message": message
        }
    }
    
    if details:
        response_data["error"]["details"] = details
    
    response = jsonify(response_data)
    response.status_code = status_code
    return response
