"""
Módulo de esquemas de validación y serialización con Marshmallow.

Define las reglas de validación, serialización y deserialización de datos para
la API usando la librería Marshmallow. Proporciona conversión bidireccional entre
objetos Python/SQLAlchemy y estructuras JSON para comunicación con clientes.

Los esquemas implementan:
    - Validación de tipos de datos y formatos
    - Restricciones de longitud y valores permitidos
    - Validaciones personalizadas a nivel de campo y schema
    - Mensajes de error personalizados y localizados
    - Conversión automática entre JSON y modelos SQLAlchemy
    - Serialización de fechas a formato ISO 8601

Example:
    Validar y deserializar datos de entrada::

        from app.schemas import cliente_schema
        
        data = {"nombre": "Juan", "email": "juan@test.com"}
        try:
            cliente = cliente_schema.load(data)
            db.session.add(cliente)
            db.session.commit()
        except ValidationError as err:
            print(err.messages)
    
    Serializar modelo a JSON::
    
        cliente = Cliente.query.get(1)
        result = cliente_schema.dump(cliente)
        # Retorna dict JSON-compatible

References:
    - Marshmallow Docs: https://marshmallow.readthedocs.io/
    - marshmallow-sqlalchemy: https://marshmallow-sqlalchemy.readthedocs.io/
    - Validation Guide: https://marshmallow.readthedocs.io/en/stable/quickstart.html
"""

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load, validates_schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .models import Cliente
from . import db


class ClienteSchema(SQLAlchemyAutoSchema):
    """
    Schema de validación y serialización para el modelo Cliente.
    
    Hereda de SQLAlchemyAutoSchema para generar automáticamente campos basados
    en las columnas del modelo Cliente. Proporciona validación robusta de datos
    de entrada y serialización consistente de respuestas.
    
    Este schema implementa:
        - Auto-generación de campos desde modelo SQLAlchemy
        - Validaciones de formato (email, longitudes)
        - Validaciones de lógica de negocio (email único, nombres válidos)
        - Conversión automática de tipos
        - Serialización de timestamps a ISO 8601
        - Mensajes de error personalizados en español
    
    Meta Configuration:
        model (Cliente): Modelo SQLAlchemy asociado al schema.
        load_instance (bool): Si True, deserialización retorna instancia del
            modelo en lugar de dict. Permite agregar directamente a sesión.
        sqla_session: Sesión de SQLAlchemy para operaciones de carga.
        ordered (bool): Mantiene orden de campos en serialización.
        include_relationships (bool): Excluye relaciones para evitar carga
            innecesaria de datos relacionados.
    
    Fields:
        id (int): Identificador único, solo lectura (dump_only).
        nombre (str): Nombre completo, requerido, 1-100 caracteres.
        email (str): Email único, requerido, formato válido, max 120 caracteres.
        telefono (str): Teléfono opcional, max 20 caracteres.
        estado (str): Estado del cliente ('activo'|'inactivo'), default 'activo'.
        fecha_creacion (datetime): Timestamp de creación, solo lectura, ISO 8601.
        fecha_actualizacion (datetime): Timestamp de actualización, solo lectura.
    
    Validations:
        - Nombre no puede ser solo espacios en blanco
        - Email debe ser formato válido y único en base de datos
        - Teléfono opcional con límite de longitud
        - Estado solo acepta 'activo' o 'inactivo'
        - Todos los campos respetan límites de columnas de BD
    
    Example:
        Deserializar con validación::
        
            schema = ClienteSchema()
            data = {
                "nombre": "María García",
                "email": "maria@empresa.com",
                "telefono": "+507 6123-4567"
            }
            try:
                cliente = schema.load(data)
                # Retorna instancia Cliente lista para guardar
            except ValidationError as err:
                print(err.messages)
                # {"email": ["Not a valid email address."]}
        
        Serializar a JSON::
        
            cliente = Cliente.query.get(1)
            result = schema.dump(cliente)
            # {
            #     "id": 1,
            #     "nombre": "María García",
            #     "email": "maria@empresa.com",
            #     ...
            # }
        
        Actualización parcial::
        
            cliente_existente = Cliente.query.get(1)
            schema = ClienteSchema()
            data = {"nombre": "Nuevo Nombre"}
            updated = schema.load(data, instance=cliente_existente, partial=True)
            # Solo actualiza campos proporcionados
    
    Note:
        - dump_only=True previene modificación accidental de campos readonly
        - load_instance=True facilita persistencia directa en base de datos
        - ordered=True garantiza orden consistente en respuestas API
        - Los errores de validación incluyen mensajes localizados
    
    Warning:
        - La validación de email único consulta la base de datos
        - Para actualizaciones, pasar instance en contexto para evitar false positives
        - ValidationError debe manejarse en la capa de controlador/ruta
    
    See Also:
        - Cliente: Modelo SQLAlchemy asociado
        - cliente_schema: Instancia global para cliente único
        - clientes_schema: Instancia global para múltiples clientes
    """
    
    class Meta:
        """
        Configuración del schema SQLAlchemyAutoSchema.
        
        Define comportamiento de generación automática de campos,
        sesión de base de datos y opciones de serialización.
        """
        model = Cliente
        load_instance = True
        sqla_session = db.session
        ordered = True
        include_relationships = False

    # Campos de solo lectura (no modificables por el usuario)
    id = fields.Int(dump_only=True)
    fecha_creacion = fields.DateTime(dump_only=True, format="iso")
    fecha_actualizacion = fields.DateTime(dump_only=True, format="iso")

    # Campo nombre con validación de longitud y mensajes personalizados
    nombre = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            "required": "El nombre es requerido",
            "validator_failed": "El nombre debe tener entre 1 y 100 caracteres"
        }
    )

    # Campo email con validación de formato y unicidad
    email = fields.Email(
        required=True,
        validate=validate.Length(max=120),
        error_messages={
            "required": "El email es requerido",
            "invalid": "El formato del email no es válido",
            "validator_failed": "El email no puede exceder 120 caracteres"
        }
    )

    # Campo teléfono opcional con límite de longitud
    telefono = fields.Str(
        allow_none=True,
        validate=validate.Length(max=20),
        error_messages={
            "validator_failed": "El teléfono no puede exceder 20 caracteres"
        }
    )

    # Campo estado con valores permitidos específicos
    estado = fields.Str(
        validate=validate.OneOf(['activo', 'inactivo']),
        load_default='activo',
        dump_default='activo',
        error_messages={
            "validator_failed": "El estado debe ser 'activo' o 'inactivo'"
        }
    )

    @validates_schema
    def validate_fields(self, data, **kwargs):
        """
        Validador a nivel de schema para reglas de negocio complejas.
        
        Se ejecuta después de las validaciones individuales de campos.
        Implementa validaciones que requieren contexto de múltiples campos
        o consultas a base de datos.
        
        Validaciones implementadas:
            1. Nombre no puede contener solo espacios en blanco
            2. Email debe ser único en la base de datos (excepto para el mismo registro)
        
        Args:
            data (dict): Diccionario con datos validados de campos individuales.
            **kwargs: Argumentos adicionales pasados por Marshmallow.
        
        Raises:
            ValidationError: Si alguna validación falla, con dict de errores
                por campo afectado.
        
        Example:
            Nombre con solo espacios::
            
                data = {"nombre": "   ", "email": "test@test.com"}
                schema.load(data)
                # ValidationError: {"nombre": ["El nombre no puede..."]}
            
            Email duplicado::
            
                # Asumiendo que ya existe juan@test.com
                data = {"nombre": "Juan", "email": "juan@test.com"}
                schema.load(data)
                # ValidationError: {"email": ["Este email ya está registrado..."]}
            
            Actualización sin error de duplicado::
            
                # Actualizar el mismo registro no debe dar error
                cliente = Cliente.query.get(1)
                data = {"email": cliente.email}  # Mismo email
                schema.load(data, instance=cliente, partial=True)
                # OK - No lanza error porque es el mismo cliente
        
        Note:
            - Se ejecuta solo si las validaciones de campos individuales pasan
            - Para actualizaciones, obtiene instance del contexto para comparar IDs
            - Acumula todos los errores antes de lanzar ValidationError
            - Consulta a BD para verificar email único puede afectar performance
        
        Performance Considerations:
            - La consulta de email único se ejecuta en cada validación
            - Considerar caché o índices de BD para optimizar
            - Solo consulta si el campo email está presente en los datos
        
        See Also:
            - @validates: Decorador para validaciones de campo único
            - ValidationError: Excepción estándar de Marshmallow
        """
        errors = {}

        # Validación de nombre: no puede ser solo espacios en blanco
        nombre = data.get('nombre')
        if nombre and not nombre.strip():
            errors['nombre'] = "El nombre no puede contener solo espacios en blanco"

        # Validación de email único en base de datos
        email = data.get('email')
        if email:
            cliente = Cliente.query.filter_by(email=email).first()
            # Obtener el cliente actual si se está actualizando (del contexto)
            instance = getattr(self, "context", {}).get("instance") if hasattr(self, "context") else None
            current_id = getattr(instance, "id", None)
            
            # Solo es error si el email existe y pertenece a otro cliente
            if cliente and cliente.id != current_id:
                errors['email'] = "Este email ya está registrado en el sistema"

        # Lanzar ValidationError si hay errores acumulados
        if errors:
            raise ValidationError(errors)

    @post_load
    def make_cliente(self, data, **kwargs):
        """
        Hook de post-procesamiento después de deserialización.
        
        Se ejecuta después de todas las validaciones exitosas. Por defecto,
        cuando load_instance=True, Marshmallow ya crea la instancia del modelo.
        Este método permite procesamiento adicional si es necesario.
        
        Args:
            data: Datos deserializados o instancia del modelo (según load_instance).
            **kwargs: Argumentos adicionales de contexto.
        
        Returns:
            Los datos o instancia sin modificar. Puede ser extendido para
            aplicar transformaciones post-validación.
        
        Example:
            Extensión para transformación adicional::
            
                @post_load
                def make_cliente(self, data, **kwargs):
                    # Normalizar nombre a title case
                    if isinstance(data, Cliente):
                        data.nombre = data.nombre.title()
                    elif isinstance(data, dict):
                        data['nombre'] = data['nombre'].title()
                    return data
        
        Note:
            - Con load_instance=True, data es ya una instancia Cliente
            - Con load_instance=False, data es un diccionario
            - Este hook es el lugar apropiado para transformaciones finales
            - Se ejecuta después de @validates_schema
        
        Use Cases:
            - Normalización de datos (mayúsculas, espacios, etc.)
            - Cálculo de campos derivados
            - Logging de creación de objetos
            - Aplicación de valores por defecto complejos
        
        See Also:
            - @pre_load: Hook antes de deserialización
            - @post_dump: Hook después de serialización
        """
        return data


# Instancias de esquemas para uso global en toda la aplicación
cliente_schema = ClienteSchema()
"""
ClienteSchema: Instancia de schema para deserialización/serialización de un solo cliente.

Usar este schema cuando se trabaja con un cliente individual en endpoints como:
    - POST /clientes (crear uno)
    - GET /clientes/<id> (obtener uno)
    - PUT /clientes/<id> (actualizar uno)

Example:
    result = cliente_schema.dump(cliente)
    cliente = cliente_schema.load(data)
"""

clientes_schema = ClienteSchema(many=True)
"""
ClienteSchema: Instancia de schema para listas de clientes (many=True).

Usar este schema cuando se trabaja con múltiples clientes en endpoints como:
    - GET /clientes (listar todos)
    - POST /clientes (crear múltiples en batch)

Example:
    results = clientes_schema.dump(lista_clientes)
    clientes = clientes_schema.load(lista_data)

Note:
    - many=True indica que se esperan/retornan listas
    - Cada item de la lista se valida individualmente
    - Un error en cualquier item cancela toda la operación
"""
