from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

# Crear la aplicación Flask
def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_mapping({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///clientes.db",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JSON_SORT_KEYS": False,
    })


    if config_object:
        app.config.from_object(config_object)


    db.init_app(app)


    # Importar y registrar blueprints y manejadores de errores
    from .routes import bp as clientes_bp
    from .errors import register_error_handlers


    app.register_blueprint(clientes_bp, url_prefix="/")
    register_error_handlers(app)


    return app