"""
Módulo de configuración de la aplicación Flask.

Este módulo implementa configuraciones basadas en clases para diferentes entornos
de ejecución (desarrollo, testing, producción). Utiliza el patrón de herencia
para compartir configuraciones comunes y especializar configuraciones por entorno.

Las configuraciones incluyen:
    - Base de datos SQLAlchemy
    - Sesiones y cookies
    - Sistema de logging
    - Opciones de API y serialización JSON

Example:
    Cargar configuración desde el factory::

        from app.config import config
        app.config.from_object(config['production'])

References:
    - Flask Configuration: https://flask.palletsprojects.com/config/
    - SQLAlchemy Engine Options: https://docs.sqlalchemy.org/en/14/core/engines.html
"""

import os
from datetime import timedelta


class Config:
    """
    Configuración base compartida por todos los entornos.
    
    Esta clase define configuraciones comunes que se aplican a todos los
    entornos (desarrollo, testing, producción). Las clases de configuración
    específicas de cada entorno heredan de esta clase base y sobrescriben
    los valores según sus necesidades.
    
    Attributes:
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Desactiva el seguimiento de
            modificaciones de SQLAlchemy para mejorar el rendimiento.
        SQLALCHEMY_ECHO (bool): Controla si SQLAlchemy imprime todas las
            sentencias SQL. Por defecto False para evitar verbosidad.
        PERMANENT_SESSION_LIFETIME (timedelta): Duración de las sesiones
            permanentes. Por defecto 7 días.
        SESSION_COOKIE_SECURE (bool): Requiere HTTPS para cookies de sesión.
            Mejora la seguridad en producción.
        SESSION_COOKIE_HTTPONLY (bool): Previene acceso JavaScript a cookies.
            Protección contra ataques XSS.
        SESSION_COOKIE_SAMESITE (str): Controla cuándo se envían cookies
            en requests cross-site. 'Lax' balancea seguridad y usabilidad.
        LOG_LEVEL (str): Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            Se obtiene de variable de entorno o por defecto INFO.
        LOG_FILE (str): Ruta del archivo de log. Por defecto 'app.log'.
        JSON_SORT_KEYS (bool): Controla ordenamiento alfabético de claves JSON.
            False preserva el orden de inserción.
        JSONIFY_PRETTYPRINT_REGULAR (bool): Formatea respuestas JSON de forma
            legible con indentación.
    
    Note:
        Esta clase no debe instanciarse directamente. Usar las subclases
        específicas de cada entorno.
    """
    
    # Base de datos
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Sesión y seguridad
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    # API y JSON
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True


class DevelopmentConfig(Config):
    """
    Configuración optimizada para desarrollo local.
    
    Activa el modo debug y utiliza SQLite como base de datos por defecto.
    El modo debug proporciona mejor información de errores y recarga automática,
    pero nunca debe usarse en producción por razones de seguridad.
    
    Attributes:
        DEBUG (bool): Activa el modo debug de Flask con recarga automática
            y mejor información de errores.
        TESTING (bool): Indica si la aplicación está en modo testing.
            False para desarrollo normal.
        SQLALCHEMY_DATABASE_URI (str): URI de conexión a la base de datos.
            Por defecto usa SQLite en carpeta instance/.
        SQLALCHEMY_ECHO (bool): Imprime todas las consultas SQL en la consola
            para facilitar debugging.
    
    Note:
        - La carpeta instance/ se crea automáticamente si no existe
        - SQLite es ideal para desarrollo pero no recomendado para producción
        - DATABASE_URL en variable de entorno sobrescribe la ruta por defecto
    
    Example:
        Activar configuración de desarrollo::
        
            export FLASK_ENV=development
            flask run
    """
    DEBUG = True
    TESTING = False

    # Crear ruta absoluta a la base de datos
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'instance', 'app.db')
    
    # Asegurar que la carpeta exista
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{db_path}')
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """
    Configuración para ejecución de tests automatizados.
    
    Utiliza base de datos en memoria para tests rápidos y aislados.
    Cada sesión de testing comienza con una base de datos limpia que
    se destruye al finalizar, garantizando independencia entre tests.
    
    Attributes:
        TESTING (bool): Activa el modo testing de Flask, modificando el
            comportamiento de manejo de errores y propagación de excepciones.
        DEBUG (bool): Mantiene debug activo para mejor información en fallos.
        SQLALCHEMY_DATABASE_URI (str): Base de datos SQLite en memoria RAM.
            Los datos no persisten entre ejecuciones.
        WTF_CSRF_ENABLED (bool): Desactiva protección CSRF para facilitar
            testing de formularios sin tokens.
    
    Note:
        - La base de datos en memoria es más rápida que disco
        - Los datos se pierden al finalizar los tests
        - No requiere limpieza manual de datos entre tests
    
    Example:
        Ejecutar tests con esta configuración::
        
            export FLASK_ENV=testing
            pytest tests/
    """
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """
    Configuración optimizada para entorno de producción.
    
    Prioriza seguridad, rendimiento y estabilidad. Requiere variables de
    entorno configuradas correctamente, especialmente DATABASE_URL.
    Incluye configuraciones de pool de conexiones para manejar alta carga.
    
    Attributes:
        DEBUG (bool): Desactiva modo debug. CRÍTICO para seguridad en producción.
        TESTING (bool): Desactiva modo testing para comportamiento normal.
        SQLALCHEMY_DATABASE_URI (str): URI de base de datos desde variable de
            entorno. Soporta PostgreSQL, MySQL, etc. REQUERIDO en producción.
        SESSION_COOKIE_SECURE (bool): Fuerza HTTPS para cookies de sesión.
            Previene interceptación de sesiones.
        SQLALCHEMY_ENGINE_OPTIONS (dict): Configuraciones del motor SQLAlchemy:
            - pool_size: Número máximo de conexiones persistentes (10 default)
            - pool_recycle: Segundos antes de reciclar conexiones (3600 = 1h)
            - pool_pre_ping: Verifica conexiones antes de usar (previene errores)
    
    Raises:
        RuntimeError: Si DATABASE_URL no está configurada en producción.
    
    Warning:
        - Nunca usar DEBUG=True en producción (expone información sensible)
        - Configurar DATABASE_URL con credenciales seguras
        - Ajustar pool_size según carga esperada y límites del servidor DB
        - Usar HTTPS obligatorio (SESSION_COOKIE_SECURE=True)
    
    Note:
        Pool size recomendado: (núcleos CPU * 2) + disco efectivo spindles.
        Para alta concurrencia, considerar ajustar pool_size y max_overflow.
    
    Example:
        Variables de entorno requeridas::
        
            export FLASK_ENV=production
            export DATABASE_URL=postgresql://user:pass@host:5432/dbname
            export SECRET_KEY=your-secret-key-here
    """
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }


# Mapeo de configuraciones
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
"""
dict: Diccionario de mapeo entre nombres de entorno y clases de configuración.

Permite seleccionar la configuración apropiada mediante string. El valor 'default'
se usa cuando no se especifica explícitamente un entorno.

Keys:
    development (DevelopmentConfig): Configuración para desarrollo local.
    testing (TestingConfig): Configuración para tests automatizados.
    production (ProductionConfig): Configuración para despliegue en producción.
    default (DevelopmentConfig): Configuración por defecto si no se especifica.

Example:
    Usar en application factory::
    
        from app.config import config
        env = os.getenv('FLASK_ENV', 'development')
        app.config.from_object(config[env])
"""
