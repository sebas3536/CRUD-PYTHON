from app import create_app
import init_db  # Este se ejecuta al importar y reinicia la DB

app = create_app()

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)("Ejectando la app en el puerto 8080")
