API de Gestión de Clientes

Este proyecto es una API REST completa para la gestión de clientes, desarrollada con el microframework Flask. Utiliza SQLAlchemy para la gestión de la base de datos y Marshmallow para la serialización y validación de datos, permitiendo un manejo eficiente y seguro de la información de los clientes.

---

Características Principales

* CRUD Completo: Permite realizar las operaciones fundamentales de creación, lectura, actualización y eliminación de clientes.
* Tecnologías Modernas: Construida con Flask, SQLAlchemy y Marshmallow, garantizando un código limpio y escalable.
* Estructura Clara: Organizada en un proyecto modular y fácil de entender.

---

Requisitos e Instalación

Requisitos Previos

Asegúrate de tener instalado Python 3.8+ y pip. Se recomienda encarecidamente usar un entorno virtual para aislar las dependencias del proyecto.

Instalación

1. Clona el repositorio en tu máquina local:
   git clone https://github.com/sebas3536/CRUD-PYTHON.git
   cd tu-repo

2. Crea y activa un entorno virtual:
   # En Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   
   # En Windows
   python -m venv venv
   venv\Scripts\activate

3. Instala las dependencias del proyecto:
   pip install -r requirements.txt

---

Ejecución

Inicializar la Base de Datos

levanta el servidor de desarrollo de Flask con:

   flask run

Esto creara la base de datos y la eliminara cada que el servidor sea ejecutado nuevamente

El servidor estará disponible por defecto en: http://127.0.0.1:8080

---

Endpoints de la API

A continuación, se listan los endpoints disponibles para interactuar con la API:

| Método HTTP | Endpoint | Descripción |

* | POST | /clientes | Crea un nuevo cliente. |
* <img width="777" height="577" alt="image" src="https://github.com/user-attachments/assets/6b94fbeb-582d-4e56-a7a8-266c3eff8d94" />

* | GET | /clientes | Obtiene una lista de todos los clientes. |
* <img width="711" height="558" alt="image" src="https://github.com/user-attachments/assets/43067ddc-5e22-4756-9d44-11abe582b4f5" />


* | GET | /clientes/<id> | Obtiene los detalles de un cliente por su ID. |
* <img width="758" height="582" alt="image" src="https://github.com/user-attachments/assets/de8f3187-d159-4e82-b4e4-e49dda99e314" />


* | PUT | /clientes/<id> | Actualiza la información de un cliente existente. |
* <img width="659" height="565" alt="image" src="https://github.com/user-attachments/assets/770d64ff-3a22-4778-b5cb-23e090732945" />


* | DELETE | /clientes/<id> | Elimina un cliente por su ID. |
* <img width="637" height="486" alt="image" src="https://github.com/user-attachments/assets/cc794f1e-7777-486f-b116-9e3fc6d5ed99" />

