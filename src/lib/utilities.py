import random
import logging
from datetime import datetime

from src.clients.open_meteo import get_weather_by_lat_long
from src.clients.poke_api import get_type


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(asctime)s %(message)s")
logger = logging.getLogger(__name__)


def get_type_by_pokemon(pokemon_data):
    """Obtengo lista de tipos de pokemones"""
    pokemon_by_types = pokemon_data.get("types", [])
    logger.info(f"Informacion pokemon de acuerdo al nombre {pokemon_by_types}")
    data = []
    for type in pokemon_by_types:
        data.append(type["type"]["name"])
    return data


def get_pokemon_by_types(pokemon_data):
    """Del listado de los pokemones de acuerdo al tipo se guarda en una lista los nombres de los pokemones"""
    pokemon_types = pokemon_data.get("pokemon", [])
    logger.info("Se obtuvo correctamente el listado de pokemones por tipo")
    data = []
    for pokemon in pokemon_types:
        data.append(pokemon["pokemon"]["name"])
    return data


def get_hour_temp_from_weather(lat, long):
    """Se genera un nuevo diccionario donde se guardará hora y temperatura relacionada de acuerdo a las coordinadas enviadas"""
    weather_data = get_weather_by_lat_long(lat, long)
    logger.info("Se obtuvo la información del clima de acuerdo a coordenadas")
    if not weather_data:
        return (
            f"No se pudo obtener el clima para la latitud {lat} y la longitud {long}",
            404,
        )
    weather_list = weather_data.get("hourly")
    logger.info("Accedo al diccionario hourly")
    times_weather = weather_list.get("time")
    logger.info("Se almaceno únicamente las horas del diccionario time")
    temp_weather = weather_list.get("temperature_2m")
    logger.info("Se almaceno la temperatura dentro del diccionario temperature_2m")
    time_temp = []
    # Genero un nuevo diccionario con diccionarios dentro que contengan horario y temperatura relacionada
    for times, temp in zip(times_weather, temp_weather):
        time_hour_dic = {
            "hora": datetime.strptime(times, "%Y-%m-%dT%H:%M"),
            "temp": temp,
        }
        time_temp.append(time_hour_dic)
    logger.info("Se generó correctamente la lista nueva de horas y temperaturas")
    return time_temp


def filter_by_letters(names):
    """Funcion para filtrar por letras"""
    letters_to_filter = {"I", "A", "M"}
    return [
        name
        for name in names
        if any(char.upper() in letters_to_filter for char in name)
    ]


def get_random_pokemons_by_letters(name):
    """Funcion para obtener un pokemon random con letras I, A o M de acuerdo al tipo"""
    pokemon_data = get_type(name)
    if not pokemon_data:
        return f"El tipo de Pokemon {name} no existe", 404
    pokemon_by_types = get_pokemon_by_types(pokemon_data)
    logger.info("Se listaron correctamente los pokemons a filtrar")
    pokemon_filter = filter_by_letters(pokemon_by_types)
    logger.info("Se filtró correctamente el pokemon")
    random_value = random.choice(pokemon_filter)
    return random_value


def find_closest_datetime(current: datetime, datetimes: list[dict]) -> dict:
    """Obtengo la fecha más cercana a la actual"""
    return min(datetimes, key=lambda dt: abs(current - dt.get("hora")))


def get_pokemon_type_by_temp(temperature: float):
    """Obtengo tipo de pokemon de acuerdo a la temperatura actual"""
    match temperature:
        case temp if temp >= 30:
            return "fire"
        case temp if 20 <= temp < 30:
            return "ground"
        case temp if 10 <= temp < 20:
            return "normal"
        case temp if 0 <= temp < 10:
            return "water"
        case temp if temp < 0:
            return "ice"
        case _:
            return "Unknown"
