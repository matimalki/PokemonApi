import logging
from apiflask import APIFlask
from src.routes import pokemon_bp


def create_app():
    app = APIFlask(__name__)
    # Configurar logger global
    logging.basicConfig(
        level=logging.INFO,  # Nivel global de logging
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Aplicación Flask inicializada")

    # Registrar blueprints
    app.register_blueprint(pokemon_bp, url_prefix="/pokemons")
    return app
