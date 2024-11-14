from src import create_app
import logging

logging.getLogger(__name__).info("Iniciando la aplicación...")

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
