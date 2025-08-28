📌 API de Gestión de Clientes con Flask

Este proyecto implementa un CRUD de clientes utilizando Flask, SQLAlchemy y Marshmallow.
Permite crear, listar, obtener, actualizar y eliminar clientes en una base de datos SQLite.

⚙️ Requisitos previos

Python 3.8 o superior

pip (gestor de paquetes de Python)

Virtualenv (opcional, recomendado)

📥 Instalación de dependencias

Clona este repositorio y entra en el directorio del proyecto:

git clone https://github.com/tu-usuario/tu-repo.git
cd tu-repo


Crea y activa un entorno virtual (opcional pero recomendado):

python -m venv venv
# En Linux/Mac
source venv/bin/activate   
# En Windows
venv\Scripts\activate


Instala las dependencias:

pip install -r requirements.txt

🗄️ Crear e inicializar la base de datos

Dentro del proyecto ya tienes el archivo init_db.py (o la función incluida en app.py) que crea la BD y las tablas.

Ejecuta:

python init_db.py


Esto generará un archivo instance/app.db con la base de datos SQLite.

▶️ Ejecutar el servidor

Levanta el servidor con:

flask run


Por defecto, estará disponible en:
👉 http://127.0.0.1:8080

(Si lo configuraste en otro puerto, cámbialo según tu app.run)

📌 Endpoints disponibles

Crear un cliente → POST /clientes
Listar todos los clientes → GET /clientes
Obtener un cliente por ID → GET /clientes/<id>
Actualizar un cliente → PUT /clientes/<id>
Eliminar un cliente → DELETE /clientes/<id>

