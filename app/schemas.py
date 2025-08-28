from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .models import Cliente
from . import db

class ClienteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Cliente
        load_instance = True
        sqla_session = db.session
        ordered = True # Para mantener el orden de los campos

    #Campos y validaciones 
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    telefono = fields.Str(validate=validate.Length(max=20))
    fecha_creacion = fields.DateTime(dump_only=True)

# Instancia de los esquemas
cliente_schema = ClienteSchema()
clientes_schema = ClienteSchema(many=True)