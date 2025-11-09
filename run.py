from app import create_app
import init_db  # Asegúrate de que esto inicialice la DB si es necesario

app = create_app()

if __name__ == "__main__":
    print("Ejecutando la app en http://127.0.0.1:8080/api/v1/clientes")
    app.run(host='127.0.0.1', port=8080, debug=True)
