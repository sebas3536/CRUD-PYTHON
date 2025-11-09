"""
Módulo de inicialización de la aplicación Flask.

Este módulo implementa el patrón Application Factory para crear instancias
configurables de la aplicación Flask. Incluye configuración de base de datos,
sistema de logging, registro de blueprints y manejo centralizado de errores.

Example:
    Crear una instancia de la aplicación::

        from app import create_app
        app = create_app('development')
        app.run()
"""

import logging
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# Inicializar la extensión de base de datos
db = SQLAlchemy()


def create_app(config_name=None):
    """
    Factory function para crear y configurar la aplicación Flask.
    
    Implementa el patrón Application Factory, permitiendo crear múltiples
    instancias de la aplicación con diferentes configuraciones. Útil para
    testing, múltiples entornos y despliegues paralelos.
    
    Args:
        config_name (str, optional): Nombre del entorno de configuración.
            Valores válidos: 'development', 'testing', 'production'.
            Si es None, se obtiene de la variable de entorno FLASK_ENV.
            Por defecto es 'development'.
    
    Returns:
        Flask: Instancia configurada de la aplicación Flask con:
            - Base de datos inicializada
            - Sistema de logging configurado
            - Blueprints registrados
            - Manejadores de errores configurados
            - Tablas de base de datos creadas
    
    Raises:
        ImportError: Si no se pueden importar los blueprints o error handlers.
        KeyError: Si config_name no existe en las configuraciones disponibles.
    
    Example:
        >>> app = create_app('production')
        >>> app.run(host='0.0.0.0', port=5000)
    """
    # Determinar configuración si no se pasa por parámetro
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Importar configuración desde el archivo config.py
    from app.config import config
    app_config = config.get(config_name, config['default'])
    
    # Crear instancia de Flask
    app = Flask(__name__)
    app.config.from_object(app_config)
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Configurar logging
    _setup_logging(app)
    
    # Registrar blueprints y manejadores de errores
    _register_blueprints(app)
    _register_error_handlers(app)
    
    # Crear tablas de base de datos dentro del contexto de la app
    with app.app_context():
        db.create_all()
    
    # Contexto para el shell de Flask
    @app.shell_context_processor
    def make_shell_context():
        """
        Proporciona contexto para 'flask shell'.
        
        Permite acceder directamente al objeto 'db' y otros recursos
        desde la consola interactiva de Flask sin necesidad de importarlos.
        
        Returns:
            dict: Diccionario con objetos disponibles en el shell.
                Incluye el objeto 'db' de SQLAlchemy.
        
        Example:
            En la terminal::
            
                $ flask shell
                >>> db
                <SQLAlchemy engine=...>
        """
        return {'db': db}

    return app


def _setup_logging(app):
    """
    Configura el sistema de logging de la aplicación.
    
    Establece dos handlers de logging: uno para archivo y otro para consola.
    El nivel de log y el archivo de salida se obtienen de la configuración
    de la aplicación.
    
    Args:
        app (Flask): Instancia de la aplicación Flask a configurar.
    
    Note:
        - El nivel de log por defecto es INFO si no se especifica en config.
        - El archivo de log por defecto es 'app.log' en el directorio raíz.
        - Formato: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    Example:
        Los logs se configuran automáticamente al crear la app::
        
            app = create_app()
            app.logger.info("Mensaje de información")
            app.logger.error("Mensaje de error")
    """
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    log_file = app.config.get('LOG_FILE', 'app.log')
    
    # Crear logger principal
    logger = logging.getLogger('app')
    logger.setLevel(log_level)
    
    # Handler para archivo
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Formato de logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Agregar handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Asignar logger a app
    app.logger = logger


def _register_blueprints(app):
    """
    Registra todos los blueprints de la aplicación.
    
    Importa y registra los blueprints que contienen las rutas de la API.
    Actualmente registra el blueprint de clientes que maneja todas las
    operaciones CRUD.
    
    Args:
        app (Flask): Instancia de la aplicación Flask donde se registrarán
            los blueprints.
    
    Raises:
        ImportError: Si no se puede importar el módulo de rutas o el blueprint.
            El error se registra en el log antes de propagarse.
    
    Note:
        Esta función es llamada automáticamente durante la inicialización
        de la aplicación. Los blueprints deben estar definidos en app.routes.
    """
    try:
        from app.routes import bp as clientes_bp
        app.register_blueprint(clientes_bp)
    except ImportError as e:
        app.logger.error(f"Error importando blueprint de clientes: {e}")
        raise


def _register_error_handlers(app):
    """
    Registra todos los manejadores de errores HTTP de la aplicación.
    
    Configura manejadores personalizados para errores HTTP comunes (404, 500, etc.)
    proporcionando respuestas JSON consistentes para toda la API.
    
    Args:
        app (Flask): Instancia de la aplicación Flask donde se registrarán
            los manejadores de errores.
    
    Raises:
        ImportError: Si no se puede importar el módulo de manejo de errores.
            El error se registra en el log antes de propagarse.
    
    Note:
        Los manejadores de errores deben estar definidos en app.errors.
        Esto asegura respuestas uniformes para todos los endpoints de la API.
    """
    try:
        from app.errors import register_error_handlers
        register_error_handlers(app)
    except ImportError as e:
        app.logger.error(f"Error importando error handlers: {e}")
        raise
