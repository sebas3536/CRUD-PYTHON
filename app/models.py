"""
Módulo de modelos de base de datos para gestión de clientes.

Define las estructuras de datos ORM usando SQLAlchemy para representar
entidades del dominio de negocio y sus relaciones. Implementa el patrón
Active Record con métodos de conveniencia para serialización y actualización.

Los modelos incluyen:
    - BaseModel: Clase abstracta con campos comunes (timestamps, ID)
    - Cliente: Entidad principal para gestión de información de clientes

Todos los modelos heredan campos de auditoría automáticos (fecha_creacion,
fecha_actualizacion) y proporcionan métodos de serialización a diccionario
para facilitar la integración con APIs REST.

Example:
    Crear y guardar un nuevo cliente::

        from app.models import Cliente
        from app import db
        
        cliente = Cliente(
            nombre="Juan Pérez",
            email="juan@example.com",
            telefono="+507 6000-0000"
        )
        db.session.add(cliente)
        db.session.commit()

References:
    - SQLAlchemy ORM: https://docs.sqlalchemy.org/en/14/orm/
    - Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/
"""

from datetime import datetime
from . import db


class BaseModel(db.Model):
    """
    Modelo base abstracto con campos comunes para auditoría.
    
    Proporciona campos estándar que todas las entidades deben tener:
    identificador único, fechas de creación y actualización. La marca
    __abstract__ previene que SQLAlchemy cree una tabla para esta clase.
    
    Esta clase implementa el patrón de herencia de tabla concreta (Concrete
    Table Inheritance), donde cada modelo hijo tiene su propia tabla completa
    con todos los campos heredados.
    
    Attributes:
        id (int): Clave primaria autoincremental única para cada registro.
        fecha_creacion (datetime): Timestamp UTC de creación del registro.
            Se establece automáticamente al insertar.
        fecha_actualizacion (datetime): Timestamp UTC de última modificación.
            Se actualiza automáticamente en cada UPDATE.
    
    Note:
        - __abstract__ = True indica que esta clase no genera tabla propia
        - Todas las fechas se almacenan en UTC para consistencia
        - La actualización automática de fecha_actualizacion usa onupdate
        - Los modelos hijos deben definir __tablename__ explícitamente
    
    Example:
        Crear modelo que hereda de BaseModel::
        
            class Producto(BaseModel):
                __tablename__ = 'productos'
                nombre = db.Column(db.String(100), nullable=False)
    
    Warning:
        No instanciar esta clase directamente. Solo usar como clase base
        para otros modelos de la aplicación.
    """
    
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_creacion = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    fecha_actualizacion = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class Cliente(BaseModel):
    """
    Modelo ORM que representa un cliente en el sistema.
    
    Almacena información esencial de clientes con campos para identificación,
    contacto y estado. Implementa validaciones a nivel de base de datos mediante
    restricciones (unique, nullable) y proporciona índices para optimizar
    consultas frecuentes.
    
    Attributes:
        id (int): Identificador único heredado de BaseModel.
        nombre (str): Nombre completo del cliente. Máximo 100 caracteres.
            Campo obligatorio indexado para búsquedas rápidas.
        email (str): Dirección de correo electrónico única. Máximo 120 caracteres.
            Usado como identificador alternativo. Indexado y con restricción UNIQUE.
        telefono (str): Número de teléfono de contacto. Máximo 20 caracteres.
            Campo opcional para permitir flexibilidad.
        estado (str): Estado actual del cliente ('activo' o 'inactivo').
            Por defecto 'activo'. Máximo 20 caracteres.
        fecha_creacion (datetime): Fecha de registro del cliente (heredado).
        fecha_actualizacion (datetime): Última modificación (heredado).
    
    Table Schema:
        - Nombre de tabla: 'clientes'
        - Índices: nombre, email
        - Restricciones únicas: email
        - Campos requeridos: nombre, email, estado
    
    Business Rules:
        - Email debe ser único en toda la base de datos
        - Estado por defecto es 'activo' al crear nuevo cliente
        - Nombre y email son obligatorios para crear cliente
        - Teléfono es opcional para flexibilidad de datos
    
    Example:
        Crear cliente completo::
        
            cliente = Cliente(
                nombre="María González",
                email="maria@empresa.com",
                telefono="+507 6123-4567",
                estado="activo"
            )
            db.session.add(cliente)
            db.session.commit()
        
        Buscar cliente por email::
        
            cliente = Cliente.query.filter_by(
                email="maria@empresa.com"
            ).first()
        
        Actualizar estado de cliente::
        
            cliente.update(estado="inactivo")
            db.session.commit()
    
    Note:
        - Los índices en nombre y email mejoran performance de búsquedas
        - La restricción UNIQUE en email previene duplicados a nivel DB
        - Los comments en columnas mejoran documentación del schema
        - datetime.utcnow usa UTC sin zona horaria (naive datetime)
    
    See Also:
        - to_dict(): Serialización a diccionario
        - update(): Actualización segura de campos
    """
    
    __tablename__ = 'clientes'
    
    nombre = db.Column(
        db.String(100),
        nullable=False,
        index=True,
        comment="Nombre completo del cliente"
    )
    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True,
        comment="Correo electrónico único"
    )
    telefono = db.Column(
        db.String(20),
        nullable=True,
        comment="Número de teléfono de contacto"
    )
    estado = db.Column(
        db.String(20),
        nullable=False,
        default='activo',
        comment="Estado actual del cliente"
    )
    
    def __repr__(self):
        """
        Representación string del objeto Cliente para debugging.
        
        Proporciona una representación legible que incluye los campos más
        importantes del cliente (id, nombre, email) para facilitar debugging
        y logging.
        
        Returns:
            str: Representación del cliente en formato
                '<Cliente {id}: {nombre} ({email})>'
        
        Example:
            >>> cliente = Cliente(id=1, nombre="Juan", email="juan@test.com")
            >>> print(cliente)
            <Cliente 1: Juan (juan@test.com)>
            >>> repr(cliente)
            '<Cliente 1: Juan (juan@test.com)>'
        
        Note:
            Este método es llamado automáticamente por print() y repr().
            Útil para logs y sesiones interactivas de debugging.
        """
        return f"<Cliente {self.id}: {self.nombre} ({self.email})>"
    
    def to_dict(self, include_timestamps=True):
        """
        Serializa el modelo Cliente a un diccionario JSON-compatible.
        
        Convierte el objeto SQLAlchemy a un diccionario estándar de Python
        que puede ser serializado a JSON para respuestas de API REST.
        Las fechas se convierten a formato ISO 8601 estándar.
        
        Args:
            include_timestamps (bool, optional): Si True, incluye fecha_creacion
                y fecha_actualizacion en el resultado. Por defecto True.
                Útil para reducir payload cuando las fechas no son necesarias.
        
        Returns:
            dict: Diccionario con todos los campos del cliente. Las fechas
                están en formato ISO 8601 string si include_timestamps=True.
        
        Example:
            Serializar con timestamps::
            
                cliente = Cliente.query.get(1)
                data = cliente.to_dict()
                # {
                #     "id": 1,
                #     "nombre": "Juan Pérez",
                #     "email": "juan@test.com",
                #     "telefono": "+507 6000-0000",
                #     "estado": "activo",
                #     "fecha_creacion": "2025-11-09T22:30:00",
                #     "fecha_actualizacion": "2025-11-09T22:30:00"
                # }
            
            Serializar sin timestamps::
            
                data = cliente.to_dict(include_timestamps=False)
                # Solo campos de negocio, sin auditoría
        
        Note:
            - El método isoformat() convierte datetime a ISO 8601
            - Telefono puede ser None si no se proporcionó
            - Este método NO persiste cambios, solo serializa
            - Compatible con jsonify() de Flask directamente
        
        See Also:
            - jsonify(): Convierte dict a Response JSON de Flask
            - ClienteSchema: Alternativa usando Marshmallow para validación
        """
        data = {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "telefono": self.telefono,
            "estado": self.estado
        }
        
        if include_timestamps:
            data.update({
                "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
                "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
            })
        
        return data
    
    def update(self, **kwargs):
        """
        Actualiza campos del cliente de forma segura y controlada.
        
        Permite actualizar múltiples campos del cliente validando que solo
        se modifiquen campos permitidos. Ignora valores None para evitar
        sobrescribir campos con datos vacíos accidentalmente.
        
        Este método implementa el patrón de actualización parcial (PATCH),
        donde solo los campos proporcionados son actualizados, manteniendo
        los demás valores intactos.
        
        Args:
            **kwargs: Pares clave-valor de campos a actualizar.
                Solo se procesan campos en la lista de campos_permitidos.
                Valores None son ignorados para prevenir sobrescritura accidental.
        
        Campos Permitidos:
            - nombre (str): Nuevo nombre del cliente
            - email (str): Nueva dirección de email
            - telefono (str): Nuevo número de teléfono
            - estado (str): Nuevo estado ('activo' o 'inactivo')
        
        Note:
            - Este método NO hace commit automático. Debe llamarse db.session.commit()
            - Campos no permitidos (id, fechas) son ignorados silenciosamente
            - Valores None son ignorados para prevenir borrado accidental
            - fecha_actualizacion se actualiza automáticamente por SQLAlchemy
            - No realiza validación de formato (usar Marshmallow schema para eso)
        
        Warning:
            - No valida formato de email o teléfono
            - No verifica si el nuevo email ya existe (puede causar IntegrityError)
            - Responsabilidad del llamador hacer commit y manejar excepciones
        
        Example:
            Actualizar múltiples campos::
            
                cliente = Cliente.query.get(1)
                cliente.update(
                    nombre="Juan Pérez Actualizado",
                    estado="inactivo"
                )
                db.session.commit()
            
            Actualizar solo email::
            
                cliente.update(email="nuevo@email.com")
                db.session.commit()
            
            Valores None son ignorados::
            
                cliente.update(nombre="Juan", telefono=None)
                # Solo actualiza nombre, telefono mantiene valor actual
        
        Raises:
            AttributeError: Si se intenta establecer un atributo no existente
                (no debería ocurrir si se usa campos_permitidos correctamente).
            IntegrityError: Si la actualización viola restricciones de BD
                (ej: email duplicado). Debe manejarse en la capa superior.
        
        See Also:
            - ClienteSchema.load(): Validación previa con Marshmallow
            - db.session.commit(): Necesario para persistir cambios
            - handle_integrity_error(): Handler para conflictos de BD
        """
        campos_permitidos = {'nombre', 'email', 'telefono', 'estado'}
        
        for key, value in kwargs.items():
            if key in campos_permitidos and value is not None:
                setattr(self, key, value)
