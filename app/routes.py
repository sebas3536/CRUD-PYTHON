from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from . import db
from .models import Cliente
from .schemas import cliente_schema, clientes_schema
from sqlalchemy.exc import IntegrityError


bp = Blueprint("clientes", __name__)


# Create a new cliente
@bp.route("/clientes", methods=["POST"])
def create_cliente():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400

    try:
        # Validar si es una lista o un solo objeto
        if isinstance(json_data, list):
            clientes = clientes_schema.load(json_data)  
            db.session.add_all(clientes)
            db.session.commit()
            return jsonify(clientes_schema.dump(clientes)), 201
        else:
        # Validar y deserializar un solo objeto
            cliente = cliente_schema.load(json_data)
            db.session.add(cliente)
            db.session.commit()
            return jsonify(cliente_schema.dump(cliente)), 201

    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Integrity error, possibly duplicate email"}), 400


# List all clientes
@bp.route("/clientes", methods=["GET"])
def list_clientes():
    clientes = Cliente.query.order_by(Cliente.id).all()
    return jsonify(clientes_schema.dump(clientes)), 200

# Get a single cliente by ID
@bp.route("/clientes/<int:id>", methods=["GET"])
def get_cliente(id):
    cliente = Cliente.query.get(id)
    if not cliente:
        return jsonify({"error": "Not Found", "message": "Cliente no encontrado."}), 404
    return jsonify(cliente_schema.dump(cliente)), 200


# Update an existing cliente
@bp.route("/clientes/<int:id>", methods=["PUT"])
def update_cliente(id):
    cliente = Cliente.query.get(id)
    if not cliente:
        return jsonify({"error": "Not Found", "message": "Cliente no encontrado."}), 404

    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400

    try:
        updated_cliente = cliente_schema.load(json_data, instance=cliente, partial=True)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Integrity error, possibly duplicate email"}), 400

    return jsonify(cliente_schema.dump(updated_cliente)), 200

# Delete a cliente
@bp.route("/clientes/<int:id>", methods=["DELETE"])
def delete_cliente(id):
    cliente = Cliente.query.get(id)
    if not cliente:
        return jsonify({"error": "Not Found", "message": "Cliente no encontrado."}), 404

    db.session.delete(cliente)
    db.session.commit()
    return jsonify({"message": "Cliente deleted successfully."}), 200
