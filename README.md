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

* | GET | /clientes | Obtiene una lista de todos los clientes. |

* | GET | /clientes/<id> | Obtiene los detalles de un cliente por su ID. |

* | PUT | /clientes/<id> | Actualiza la información de un cliente existente. |

* | DELETE | /clientes/<id> | Elimina un cliente por su ID. |
