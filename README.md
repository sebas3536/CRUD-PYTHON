# API de Gestión de Clientes

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-orange)](LICENSE)

## 📋 Descripción

API REST para la gestión integral de clientes. Construida con arquitectura modular y escalable, proporciona operaciones CRUD completas con validación robusta, manejo de errores centralizado y logging integrado.

## ✨ Características Principales

- **CRUD Completo** - Operaciones Create, Read, Update, Delete totalmente implementadas
- **Validación Robusta** - Marshmallow para serialización y validación de datos
- **Gestión de Errores** - Manejo centralizado y consistente de excepciones
- **Paginación** - Soporte para listados paginados y filtrados
- **ORM Potente** - SQLAlchemy para operaciones de base de datos
- **Logging** - Sistema de logging integrado para auditoría
- **Documentación** - Docstrings y comentarios completos en el código
- **Arquitectura Modular** - Código organizado y altamente escalable

## 🛠 Tecnologías

| Tecnología | Versión | Descripción |
|-----------|---------|------------|
| Python | 3.8+ | Lenguaje principal |
| Flask | 2.0+ | Framework web |
| SQLAlchemy | 1.4+ | ORM para base de datos |
| Marshmallow | 3.0+ | Validación y serialización |
| SQLite | 3.0+ | Base de datos (desarrollo) |

## 📦 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes)
- Git

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/sebas3536/CRUD-PYTHON.git
cd CRUD-PYTHON
```

2. **Crear entorno virtual**
```bash
# En Linux/macOS
python3 -m venv venv
source venv/bin/activate

# En Windows
python -m venv venv
venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

## 🚀 Uso

### Iniciar el Servidor

```bash
# Desarrollo
python run.py

# Producción
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

El servidor estará disponible en `http://127.0.0.1:8080/api/v1/clientes`

> **Nota:** La base de datos se crea automáticamente al iniciar. En desarrollo, los datos se resetean con cada reinicio.

## 📚 Documentación de API

### Base URL
```
http://localhost:8080/api/v1
```

### Endpoints

#### 1. Crear Cliente(s)
```http
POST /clientes
Content-Type: application/json

# Cliente único
{
  "nombre": "Juan Pérez García",
  "email": "juan@ejemplo.com",
  "telefono": "+34 612 345 678",
  "estado": "activo"
}

# Múltiples clientes
[
  {
    "nombre": "María López",
    "email": "maria@ejemplo.com",
    "telefono": "+34 612 345 679"
  },
  {
    "nombre": "Carlos Rodríguez",
    "email": "carlos@ejemplo.com"
  }
]
```

**Respuesta (201 Created):**
```json
{
  "success": true,
  "message": "Cliente creado exitosamente",
  "data": {
    "id": 1,
    "nombre": "Juan Pérez García",
    "email": "juan@ejemplo.com",
    "telefono": "+34 612 345 678",
    "estado": "activo",
    "fecha_creacion": "2025-01-20T15:30:45",
    "fecha_actualizacion": "2025-01-20T15:30:45"
  }
}
```

#### 2. Obtener Todos los Clientes
```http
GET /clientes?page=1&per_page=10&estado=activo
```

**Parámetros de Query:**
- `page` (int): Número de página (default: 1)
- `per_page` (int): Resultados por página (default: 10, máximo: 100)
- `estado` (string): Filtrar por estado (activo/inactivo)

**Respuesta (200 OK):**
```json
{
  "success": true,
  "message": "Listado de clientes obtenido",
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 25,
    "pages": 3
  },
  "data": [
    {
      "id": 1,
      "nombre": "Juan Pérez",
      "email": "juan@ejemplo.com",
      "telefono": "+34 612 345 678",
      "estado": "activo",
      "fecha_creacion": "2025-01-20T15:30:45",
      "fecha_actualizacion": "2025-01-20T15:30:45"
    }
  ]
}
```

#### 3. Obtener Cliente por ID
```http
GET /clientes/1
```

**Respuesta (200 OK):**
```json
{
  "success": true,
  "message": "Cliente obtenido exitosamente",
  "data": {
    "id": 1,
    "nombre": "Juan Pérez",
    "email": "juan@ejemplo.com",
    "telefono": "+34 612 345 678",
    "estado": "activo",
    "fecha_creacion": "2025-01-20T15:30:45",
    "fecha_actualizacion": "2025-01-20T15:30:45"
  }
}
```

#### 4. Actualizar Cliente
```http
PUT /clientes/1
Content-Type: application/json

{
  "nombre": "Juan Pérez García Actualizado",
  "telefono": "+34 612 999 999",
  "estado": "inactivo"
}
```

**Respuesta (200 OK):**
```json
{
  "success": true,
  "message": "Cliente actualizado exitosamente",
  "data": {
    "id": 1,
    "nombre": "Juan Pérez García Actualizado",
    "email": "juan@ejemplo.com",
    "telefono": "+34 612 999 999",
    "estado": "inactivo",
    "fecha_creacion": "2025-01-20T15:30:45",
    "fecha_actualizacion": "2025-01-20T16:45:20"
  }
}
```

#### 5. Eliminar Cliente
```http
DELETE /clientes/1
```

**Respuesta (200 OK):**
```json
{
  "success": true,
  "message": "Cliente eliminado exitosamente"
}
```

### Códigos de Error

| Código | Tipo | Descripción |
|--------|------|------------|
| 400 | BAD_REQUEST | Solicitud mal formada o datos ausentes |
| 404 | NOT_FOUND | Recurso no encontrado |
| 409 | INTEGRITY_ERROR | Violación de restricciones (email duplicado) |
| 422 | VALIDATION_ERROR | Datos no válidos según las reglas de validación |
| 500 | INTERNAL_SERVER_ERROR | Error interno del servidor |

### Ejemplos con cURL

**Crear cliente:**
```bash
curl -X POST http://localhost:5000/api/v1/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Pérez",
    "email": "juan@ejemplo.com",
    "telefono": "+34 612 345 678"
  }'
```

**Obtener todos los clientes:**
```bash
curl http://localhost:5000/api/v1/clientes?page=1&per_page=5
```

**Obtener cliente por ID:**
```bash
curl http://localhost:5000/api/v1/clientes/1
```

**Actualizar cliente:**
```bash
curl -X PUT http://localhost:5000/api/v1/clientes/1 \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Pérez Actualizado",
    "estado": "inactivo"
  }'
```

**Eliminar cliente:**
```bash
curl -X DELETE http://localhost:5000/api/v1/clientes/1
```

## 📁 Estructura del Proyecto

```
CRUD-PYTHON/
├── app.py                    # Punto de entrada de la aplicación
├── config.py                 # Configuración de la aplicación
├── requirements.txt          # Dependencias del proyecto
├── .env.example             # Variables de entorno ejemplo
├── .gitignore               # Archivos ignorados por git
├── README.md                # Este archivo
├── LICENSE                  # Licencia MIT
│
├── app/
│   ├── __init__.py          # Inicialización del paquete
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Esquemas Marshmallow
│   ├── error_handlers.py    # Gestión centralizada de errores
│   │
│   └── routes/
│       ├── __init__.py
│       └── clientes.py      # Endpoints de clientes
│
├── instance/
│   └── app.db               # Base de datos SQLite (generada)
│
└── tests/
    ├── __init__.py
    ├── test_clientes.py     # Tests unitarios
    └── conftest.py          # Configuración pytest
```

## 🔒 Validación de Datos

El sistema implementa validación exhaustiva en múltiples niveles:

### Reglas de Validación

**Cliente:**
- **Nombre**: Requerido, 1-100 caracteres, no solo espacios
- **Email**: Requerido, formato válido, 1-120 caracteres, único en BD
- **Teléfono**: Opcional, máximo 20 caracteres
- **Estado**: Opcional, valores permitidos: "activo", "inactivo"

### Ejemplo de Respuesta con Error de Validación

```json
{
  "success": false,
  "error": {
    "type": "VALIDATION_ERROR",
    "message": "Los datos no cumplen con los requisitos de validación",
    "details": {
      "nombre": ["El nombre es requerido"],
      "email": ["El formato del email no es válido"]
    }
  }
}
```

## 📋 Requisitos (requirements.txt)

```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
SQLAlchemy==2.0.20
marshmallow==3.20.1
marshmallow-sqlalchemy==0.29.0
python-dotenv==1.0.0
gunicorn==21.2.0
```


## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto (`git clone https://github.com/tu-usuario/CRUD-PYTHON.git`)
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Estándares de Código

- Seguir PEP 8
- Incluir docstrings en funciones y clases
- Escribir tests para nuevas funcionalidades
- Actualizar documentación


## 👤 Autor

**Sebastián**

- GitHub: [@sebas3536](https://github.com/sebas3536)
- Email: delahozpablo005@gmail.com

## 🙏 Agradecimientos

- Flask y su comunidad
- SQLAlchemy
- Marshmallow
- Comunidad open source

---

**Última actualización:** Noviembre 2025 | **Versión:** 1.0.0