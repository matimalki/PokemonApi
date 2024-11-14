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
    logger.info("listado de pokemones por tipo", pokemon_types)
    data = []
    for pokemon in pokemon_types:
        data.append(pokemon["pokemon"]["name"])
    return data


def get_hour_temp_from_weather(lat, long):
    """Se genera un nuevo diccionario donde se guardará hora y temperatura relacionada de acuerdo a las coordinadas enviadas"""
    weather_data = get_weather_by_lat_long(lat, long)
    logger.info(weather_data)
    if not weather_data:
        return (
            f"No se pudo obtener el clima para la latitud {lat} y la longitud {long}",
            404,
        )
    lista_weather = weather_data.get("hourly")
    logger.info(lista_weather)
    times_weather = lista_weather.get("time")
    logger.info(times_weather)
    temp_weather = lista_weather.get("temperature_2m")
    logger.info(temp_weather)
    hora_temp = []
    logger.info(hora_temp)
    # Genero un nuevo diccionario con diccionarios dentro que contengan horario y temperatura relacionada
    for times, temp in zip(times_weather, temp_weather):
        time_hour_dic = {
            "hora": datetime.strptime(times, "%Y-%m-%dT%H:%M"),
            "temp": temp,
        }
        hora_temp.append(time_hour_dic)
    return hora_temp


def filter_by_letters(names):
    """Funcion para filtrar por letras"""
    letras_a_filtrar = {"I", "A", "M"}
    return [
        name for name in names if any(char.upper() in letras_a_filtrar for char in name)
    ]


def get_random_pokemons_by_letters(name):
    """Funcion para obtener un pokemon random con letras I, A o M de acuerdo al tipo"""
    pokemon_data = get_type(name)
    if not pokemon_data:
        return f"El tipo de Pokemon {name} no existe", 404
    pokemon_by_types = get_pokemon_by_types(pokemon_data)
    logger.info("Listado de pokemones a filtrar", pokemon_by_types)
    filtro_pokemon = filter_by_letters(pokemon_by_types)
    logger.info("Listado de pokemones filtrados", filtro_pokemon)
    valor_aleatorio = random.choice(filtro_pokemon)
    return valor_aleatorio



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
