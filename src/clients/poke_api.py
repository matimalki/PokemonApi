import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(asctime)s %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://pokeapi.co/api/v2"


def get_pokemon_by_name(name: str):
    """Llamada a la api para consumir lista de pokemones"""
    response = requests.get(f"{BASE_URL}/pokemon/{name}")
    logger.info("Consumiendo Api")
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_type(name: str):
    """Llamada a la api para obtener listado de pokemones de acuerdo al tipo"""
    response = requests.get(f"{BASE_URL}/type/{name}")
    logger.info("Consumiendo Api")
    if response.status_code == 200:
        return response.json()
    else:
        return None
