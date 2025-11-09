"""
Módulo de endpoints REST API para gestión de clientes.

Implementa una API RESTful completa con operaciones CRUD (Create, Read, Update,
Delete) para el recurso Cliente. Todos los endpoints siguen las convenciones
REST estándar y retornan respuestas JSON estructuradas.

El módulo utiliza Flask Blueprints para modularización y organización del código,
permitiendo separación de funcionalidades y versionado de API mediante prefijos.

Endpoints Disponibles:
    POST   /api/v1/clientes       - Crear uno o múltiples clientes
    GET    /api/v1/clientes       - Listar clientes con paginación
    GET    /api/v1/clientes/<id>  - Obtener cliente específico
    PUT    /api/v1/clientes/<id>  - Actualizar cliente (parcial/completo)
    DELETE /api/v1/clientes/<id>  - Eliminar cliente

Características:
    - Validación automática con Marshmallow schemas
    - Manejo centralizado de errores con APIError
    - Soporte para operaciones batch (múltiples clientes)
    - Paginación con parámetros configurables
    - Filtrado por estado (activo/inactivo)
    - Actualización parcial (PATCH-like behavior)
    - Respuestas JSON estandarizadas

Example:
    Registrar blueprint en la aplicación::

        from app.routes import bp as clientes_bp
        app.register_blueprint(clientes_bp)

References:
    - Flask Blueprints: https://flask.palletsprojects.com/blueprints/
    - REST API Best Practices: https://restfulapi.net/
    - HTTP Status Codes: https://httpstatuses.com/
"""

from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import Cliente
from app.schemas import cliente_schema, clientes_schema
from app.errors import APIError


bp = Blueprint(
    "clientes",
    __name__,
    url_prefix="/api/v1/clientes",
)
"""
Blueprint para agrupar todos los endpoints relacionados con clientes.

El blueprint utiliza el prefijo '/api/v1/clientes' para todas las rutas,
facilitando el versionado de API y la organización modular del código.

Attributes:
    name (str): Identificador único del blueprint ('clientes').
    url_prefix (str): Prefijo común para todas las rutas del blueprint.
"""


@bp.route("", methods=["POST"])
def create_cliente():
    """
    Endpoint para crear uno o múltiples clientes en el sistema.
    
    Acepta tanto un objeto JSON único como una lista de objetos para
    permitir creación batch. Valida todos los datos usando Marshmallow
    schemas antes de la inserción en base de datos.
    
    Request Body (Single):
        {
            "nombre": "Juan Pérez",
            "email": "juan@example.com",
            "telefono": "+507 6000-0000",
            "estado": "activo"
        }
    
    Request Body (Multiple):
        [
            {"nombre": "Cliente 1", "email": "c1@test.com"},
            {"nombre": "Cliente 2", "email": "c2@test.com"}
        ]
    
    Returns:
        Response (201 Created): Cliente(s) creado(s) exitosamente con datos
            completos incluyendo IDs generados y timestamps.
            
            Single client response:
            {
                "success": true,
                "message": "Cliente creado exitosamente",
                "data": {
                    "id": 1,
                    "nombre": "Juan Pérez",
                    "email": "juan@example.com",
                    "telefono": "+507 6000-0000",
                    "estado": "activo",
                    "fecha_creacion": "2025-11-09T22:30:00",
                    "fecha_actualizacion": "2025-11-09T22:30:00"
                }
            }
            
            Multiple clients response:
            {
                "success": true,
                "message": "Se crearon 2 clientes exitosamente",
                "data": [...]
            }
    
    Raises:
        APIError (400 Bad Request): Si no se proporcionan datos o la lista
            está vacía.
        APIError (422 Unprocessable Entity): Si los datos no pasan la
            validación de Marshmallow (formato email inválido, campos faltantes).
        APIError (409 Conflict): Si el email ya existe en el sistema
            (violación de restricción UNIQUE).
    
    HTTP Status Codes:
        201: Cliente(s) creado(s) exitosamente
        400: Request body vacío o lista vacía
        409: Email duplicado (violación de integridad)
        422: Errores de validación de datos
    
    Example:
        Crear cliente único::
        
            POST /api/v1/clientes
            Content-Type: application/json
            
            {
                "nombre": "María García",
                "email": "maria@empresa.com",
                "telefono": "+507 6123-4567"
            }
        
        Crear múltiples clientes::
        
            POST /api/v1/clientes
            Content-Type: application/json
            
            [
                {"nombre": "Cliente A", "email": "a@test.com"},
                {"nombre": "Cliente B", "email": "b@test.com"}
            ]
    
    Note:
        - El campo 'estado' por defecto es 'activo' si no se especifica
        - Todos los clientes en operaciones batch se crean en una transacción
        - Si falla la validación de uno, se rechaza toda la operación batch
        - El email debe ser único en toda la base de datos
    
    See Also:
        - cliente_schema: Schema de validación para cliente único
        - clientes_schema: Schema para múltiples clientes
        - Cliente.to_dict(): Método alternativo de serialización
    """
    json_data = request.get_json()
    
    if not json_data:
        raise APIError(
            "No se proporcionaron datos de entrada",
            status_code=400
        )
    
    try:
        # Procesar múltiples clientes
        if isinstance(json_data, list):
            if not json_data:
                raise APIError(
                    "La lista de clientes no puede estar vacía",
                    status_code=400
                )
            
            clientes = clientes_schema.load(json_data)
            db.session.add_all(clientes)
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": f"Se crearon {len(clientes)} clientes exitosamente",
                "data": clientes_schema.dump(clientes)
            }), 201
        
        # Procesar cliente único
        else:
            cliente = cliente_schema.load(json_data)
            db.session.add(cliente)
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "Cliente creado exitosamente",
                "data": cliente_schema.dump(cliente)
            }), 201
    
    except ValidationError as err:
        raise APIError(
            "Error en la validación de datos",
            status_code=422,
            details=err.messages
        )
    except IntegrityError:
        db.session.rollback()
        raise APIError(
            "El email ya existe en el sistema",
            status_code=409
        )


@bp.route("", methods=["GET"])
def list_clientes():
    """
    Endpoint para obtener listado paginado de clientes.
    
    Retorna una lista paginada de clientes con soporte para filtrado por
    estado. La paginación previene sobrecarga en respuestas con muchos
    registros y mejora el rendimiento del API.
    
    Query Parameters:
        page (int, optional): Número de página a obtener. Debe ser >= 1.
            Default: 1.
        per_page (int, optional): Cantidad de resultados por página.
            Rango válido: 1-100. Default: 10.
        estado (str, optional): Filtrar clientes por estado.
            Valores válidos: 'activo', 'inactivo'. Default: todos los estados.
    
    Returns:
        Response (200 OK): Lista de clientes con metadatos de paginación.
            
            {
                "success": true,
                "message": "Listado de clientes obtenido",
                "pagination": {
                    "page": 1,
                    "per_page": 10,
                    "total": 45,
                    "pages": 5
                },
                "data": [
                    {
                        "id": 1,
                        "nombre": "Juan Pérez",
                        "email": "juan@example.com",
                        "telefono": "+507 6000-0000",
                        "estado": "activo",
                        "fecha_creacion": "2025-11-09T22:30:00",
                        "fecha_actualizacion": "2025-11-09T22:30:00"
                    },
                    ...
                ]
            }
    
    Raises:
        APIError (400 Bad Request): Si los parámetros de paginación son
            inválidos (page < 1, per_page fuera de rango 1-100) o si el
            estado no es válido.
    
    HTTP Status Codes:
        200: Listado obtenido exitosamente
        400: Parámetros de query inválidos
    
    Example:
        Obtener primera página con valores default::
        
            GET /api/v1/clientes
        
        Obtener página específica con más resultados::
        
            GET /api/v1/clientes?page=2&per_page=20
        
        Filtrar solo clientes activos::
        
            GET /api/v1/clientes?estado=activo
        
        Combinar paginación y filtrado::
        
            GET /api/v1/clientes?page=1&per_page=50&estado=inactivo
    
    Pagination Details:
        - page: Número de página actual solicitada
        - per_page: Cantidad de items retornados
        - total: Total de registros que coinciden con el filtro
        - pages: Total de páginas disponibles
    
    Note:
        - Si se solicita una página fuera de rango, retorna lista vacía
        - Los resultados se ordenan por ID ascendente
        - El límite máximo de per_page es 100 para prevenir sobrecarga
        - error_out=False previene excepción 404 en páginas vacías
        - Los filtros son case-sensitive
    
    Performance:
        - Índices en 'nombre' y 'email' mejoran velocidad de búsqueda
        - Paginación reduce tamaño de respuesta y uso de memoria
        - Considerar caching para listados frecuentes sin filtros
    
    See Also:
        - Cliente.query: Constructor de queries SQLAlchemy
        - flask_sqlalchemy.Pagination: Objeto de paginación retornado
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    estado = request.args.get('estado', None, type=str)
    
    # Validar parámetros
    if page < 1:
        raise APIError("El número de página debe ser mayor a 0", status_code=400)
    if per_page < 1 or per_page > 100:
        raise APIError("El número de resultados debe estar entre 1 y 100", status_code=400)
    
    # Construir consulta
    query = Cliente.query
    
    if estado:
        if estado not in ['activo', 'inactivo']:
            raise APIError("El estado debe ser 'activo' o 'inactivo'", status_code=400)
        query = query.filter_by(estado=estado)
    
    # Ejecutar paginación
    paginated = query.order_by(Cliente.id).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return jsonify({
        "success": True,
        "message": "Listado de clientes obtenido",
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": paginated.total,
            "pages": paginated.pages
        },
        "data": clientes_schema.dump(paginated.items)
    }), 200


@bp.route("/<int:id>", methods=["GET"])
def get_cliente(id):
    """
    Endpoint para obtener los detalles completos de un cliente específico.
    
    Recupera toda la información de un cliente identificado por su ID único.
    Útil para obtener datos completos antes de actualizar o para mostrar
    perfil detallado en interfaces de usuario.
    
    Path Parameters:
        id (int): Identificador único del cliente. Debe ser un entero positivo
            que corresponda a un cliente existente en la base de datos.
    
    Returns:
        Response (200 OK): Datos completos del cliente solicitado.
            
            {
                "success": true,
                "message": "Cliente obtenido exitosamente",
                "data": {
                    "id": 5,
                    "nombre": "Ana López",
                    "email": "ana@example.com",
                    "telefono": "+507 6555-1234",
                    "estado": "activo",
                    "fecha_creacion": "2025-11-08T15:20:00",
                    "fecha_actualizacion": "2025-11-09T10:45:00"
                }
            }
    
    Raises:
        APIError (404 Not Found): Si no existe un cliente con el ID
            proporcionado en la base de datos.
    
    HTTP Status Codes:
        200: Cliente encontrado y retornado exitosamente
        404: Cliente no encontrado
    
    Example:
        Obtener cliente con ID 5::
        
            GET /api/v1/clientes/5
        
        Respuesta exitosa (200):
            Cliente encontrado, retorna datos completos
        
        Respuesta de error (404):
            {
                "success": false,
                "error": {
                    "type": "API_ERROR",
                    "message": "No se encontró cliente con ID 5"
                }
            }
    
    Note:
        - El ID debe ser un entero válido en la ruta
        - Flask convierte automáticamente el parámetro a int
        - Si el ID no es numérico, Flask retorna 404 automáticamente
        - Incluye todos los campos, incluyendo timestamps de auditoría
    
    Use Cases:
        - Obtener datos para formulario de edición
        - Mostrar perfil completo de cliente
        - Verificar existencia antes de operaciones
        - Obtener datos actualizados después de modificaciones
    
    See Also:
        - update_cliente(): Actualizar datos del cliente
        - delete_cliente(): Eliminar cliente
        - Cliente.query.get(): Método de consulta por ID
    """
    cliente = Cliente.query.get(id)
    
    if not cliente:
        raise APIError(
            f"No se encontró cliente con ID {id}",
            status_code=404
        )
    
    return jsonify({
        "success": True,
        "message": "Cliente obtenido exitosamente",
        "data": cliente_schema.dump(cliente)
    }), 200


@bp.route("/<int:id>", methods=["PUT"])
def update_cliente(id):
    """
    Endpoint para actualizar información de un cliente existente.
    
    Soporta actualización parcial (estilo PATCH) donde solo los campos
    proporcionados en el request body son actualizados, manteniendo el
    resto de valores intactos. Útil para modificaciones selectivas sin
    necesidad de enviar todos los campos.
    
    Path Parameters:
        id (int): Identificador único del cliente a actualizar.
    
    Request Body:
        Objeto JSON con los campos a actualizar. Todos los campos son
        opcionales (actualización parcial):
        
        {
            "nombre": "Juan Pérez Actualizado",
            "email": "nuevo@example.com",
            "telefono": "+507 6999-8888",
            "estado": "inactivo"
        }
    
    Returns:
        Response (200 OK): Cliente actualizado con datos completos.
            
            {
                "success": true,
                "message": "Cliente actualizado exitosamente",
                "data": {
                    "id": 5,
                    "nombre": "Juan Pérez Actualizado",
                    "email": "nuevo@example.com",
                    "telefono": "+507 6999-8888",
                    "estado": "inactivo",
                    "fecha_creacion": "2025-11-08T15:20:00",
                    "fecha_actualizacion": "2025-11-09T22:50:00"
                }
            }
    
    Raises:
        APIError (400 Bad Request): Si no se proporciona ningún dato en
            el request body.
        APIError (404 Not Found): Si el cliente con el ID especificado
            no existe en la base de datos.
        APIError (422 Unprocessable Entity): Si los datos no pasan la
            validación de Marshmallow.
        APIError (409 Conflict): Si el nuevo email ya está siendo usado
            por otro cliente (violación de UNIQUE constraint).
    
    HTTP Status Codes:
        200: Cliente actualizado exitosamente
        400: Request body vacío
        404: Cliente no encontrado
        409: Email duplicado
        422: Errores de validación
    
    Example:
        Actualizar solo el estado::
        
            PUT /api/v1/clientes/5
            Content-Type: application/json
            
            {"estado": "inactivo"}
        
        Actualizar múltiples campos::
        
            PUT /api/v1/clientes/5
            Content-Type: application/json
            
            {
                "nombre": "Juan Pérez García",
                "telefono": "+507 6111-2222",
                "email": "juan.nuevo@example.com"
            }
        
        Error de validación (422)::
        
            PUT /api/v1/clientes/5
            {"email": "invalid-email"}
            
            Response:
            {
                "success": false,
                "error": {
                    "type": "VALIDATION_ERROR",
                    "message": "Error en la validación...",
                    "details": {
                        "email": ["Not a valid email address."]
                    }
                }
            }
    
    Note:
        - Usa partial=True en Marshmallow para permitir actualización parcial
        - fecha_actualizacion se actualiza automáticamente por SQLAlchemy
        - Los campos no incluidos en el request mantienen sus valores actuales
        - El ID no puede ser modificado (es inmutable)
        - Validación de email único se ejecuta a nivel de base de datos
    
    Best Practices:
        - Enviar solo campos que cambiarán (actualización parcial)
        - Validar datos en cliente antes de enviar request
        - Manejar código 409 para emails duplicados en UI
        - Refrescar datos en cliente después de actualización exitosa
    
    Warning:
        - Cambiar el email puede afectar autenticación si se usa como login
        - Cambiar estado a 'inactivo' puede afectar lógica de negocio
        - No hay soft-delete: use estado='inactivo' en lugar de DELETE
    
    See Also:
        - cliente_schema.load(): Validación con partial=True
        - get_cliente(): Obtener datos actuales antes de modificar
        - Cliente.update(): Método del modelo (alternativa)
    """
    cliente = Cliente.query.get(id)
    
    if not cliente:
        raise APIError(
            f"No se encontró cliente con ID {id}",
            status_code=404
        )
    
    json_data = request.get_json()
    
    if not json_data:
        raise APIError(
            "No se proporcionaron datos de entrada",
            status_code=400
        )
    
    try:
        # Cargar datos con actualización parcial
        updated_cliente = cliente_schema.load(
            json_data,
            instance=cliente,
            partial=True
        )
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Cliente actualizado exitosamente",
            "data": cliente_schema.dump(updated_cliente)
        }), 200
    
    except ValidationError as err:
        raise APIError(
            "Error en la validación de datos",
            status_code=422,
            details=err.messages
        )
    except IntegrityError:
        db.session.rollback()
        raise APIError(
            "El email ya existe en el sistema",
            status_code=409
        )


@bp.route("/<int:id>", methods=["DELETE"])
def delete_cliente(id):
    """
    Endpoint para eliminar permanentemente un cliente del sistema.
    
    Realiza eliminación física (hard delete) del registro de la base de datos.
    Esta operación es irreversible. Para eliminación lógica, considerar
    actualizar el estado a 'inactivo' usando el endpoint PUT.
    
    Path Parameters:
        id (int): Identificador único del cliente a eliminar.
    
    Returns:
        Response (200 OK): Confirmación de eliminación exitosa.
            
            {
                "success": true,
                "message": "Cliente eliminado exitosamente"
            }
    
    Raises:
        APIError (404 Not Found): Si el cliente con el ID especificado
            no existe en la base de datos.
        APIError (500 Internal Server Error): Si ocurre un error inesperado
            durante la eliminación (por ejemplo, violación de integridad
            referencial si el cliente tiene relaciones).
    
    HTTP Status Codes:
        200: Cliente eliminado exitosamente
        404: Cliente no encontrado
        500: Error al eliminar (posibles dependencias)
    
    Example:
        Eliminar cliente exitosamente::
        
            DELETE /api/v1/clientes/5
            
            Response (200):
            {
                "success": true,
                "message": "Cliente eliminado exitosamente"
            }
        
        Cliente no encontrado::
        
            DELETE /api/v1/clientes/999
            
            Response (404):
            {
                "success": false,
                "error": {
                    "type": "API_ERROR",
                    "message": "No se encontró cliente con ID 999"
                }
            }
    
    Warning:
        - Esta operación es IRREVERSIBLE - no hay recuperación de datos
        - Considerar soft-delete (estado='inactivo') para datos importantes
        - Puede fallar si el cliente tiene relaciones en otras tablas
        - No se retornan los datos del cliente eliminado
        - Eliminar muchos registros puede afectar performance
    
    Note:
        - Se hace rollback automático si ocurre error durante eliminación
        - El error se registra en logs antes de retornar respuesta 500
        - Verificar permisos de usuario antes de permitir eliminación
        - Considerar auditoría de eliminaciones en ambientes de producción
    
    Best Practices:
        - Implementar confirmación en UI antes de eliminar
        - Usar soft-delete (estado='inactivo') en lugar de hard-delete
        - Mantener backups regulares de la base de datos
        - Auditar quién y cuándo elimina registros
        - Verificar dependencias antes de permitir eliminación
    
    Alternative Approach:
        Para eliminación lógica (recomendado)::
        
            PUT /api/v1/clientes/5
            {"estado": "inactivo"}
            
            # Permite recuperación posterior y mantiene histórico
    
    Database Considerations:
        - Si existen foreign keys, puede fallar con IntegrityError
        - Considerar ON DELETE CASCADE para eliminar dependencias
        - O usar ON DELETE RESTRICT para prevenir eliminación accidental
    
    See Also:
        - update_cliente(): Alternativa para soft-delete
        - get_cliente(): Verificar datos antes de eliminar
        - db.session.rollback(): Reversión en caso de error
    """
    cliente = Cliente.query.get(id)
    
    if not cliente:
        raise APIError(
            f"No se encontró cliente con ID {id}",
            status_code=404
        )
    
    try:
        db.session.delete(cliente)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Cliente eliminado exitosamente"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al eliminar cliente {id}: {e}")
        raise APIError(
            "Error al eliminar el cliente",
            status_code=500
        )
