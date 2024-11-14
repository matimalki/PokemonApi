from flask import jsonify, Blueprint, request
import random
import logging
from datetime import datetime

from src.clients.poke_api import get_pokemon_by_name
from src.lib.utilities import (
    find_closest_datetime,
    get_hour_temp_from_weather,
    get_pokemon_by_types,
    get_pokemon_type_by_temp,
    get_random_pokemons_by_letters,
    get_type,
    get_type_by_pokemon,
)


pokemon_bp = Blueprint("pokemon_bp", __name__)
logger = logging.getLogger("pokemon_routes")


@pokemon_bp.route("/<name>", methods=["GET"])
def get_pokemon(name):
    pokemon_data = get_pokemon_by_name(name)
    if not pokemon_data:
        return f"El Pokemon {name} no existe", 404
    pokemon_types = get_type_by_pokemon(pokemon_data)
    return {"pokemon_types": pokemon_types, "pokemon_name": name}


@pokemon_bp.route("/types/<name>", methods=["GET"])
def get_random_pokemon_by_type(name):
    """De acuerdo al tipo de pokemon colocado en el endpoint, arroja un nombre random de ese mismo tipo"""
    pokemon_data = get_type(name)
    if not pokemon_data:
        return f"El tipo de Pokemon {name} no existe", 404
    pokemon_by_types = get_pokemon_by_types(pokemon_data)
    logger.info(
        f"tipo de pokemon: {name} \n Listado de pokemones por tipo seleccionado {pokemon_by_types}"
    )
    valor_aleatorio = random.choice(pokemon_by_types)
    return jsonify({"pokemon_name": valor_aleatorio})


@pokemon_bp.route("/largest_name/<pokemon_type>", methods=["GET"])
def get_largest_name_by_type(pokemon_type):
    """Se obtiene el nombre más largo de pokemon de acuerdo a su tipo especificado en el endpoint"""
    pokemon_data = get_type(pokemon_type)
    if not pokemon_data:
        return f"El tipo de Pokemon {pokemon_type} no existe", 404
    pokemon_by_types = get_pokemon_by_types(pokemon_data)
    logger.info("Listado de pokemones por tipo seleccionado", pokemon_by_types)
    return {"pokemon_name": max(pokemon_by_types, key=len)}


@pokemon_bp.route("/random_by_temp", methods=["GET"])
def random_pokemon():
    lat = request.args.get("lat")
    long = request.args.get("long")
    if not lat or not long:
        return "Falta latitud y longitud", 400
    # guardo diccionario con hora y temperatura agrupada
    lista_horas_y_temp = get_hour_temp_from_weather(float(lat), float(long))
    logger.info("Listado de horas y temp asociadas", lista_horas_y_temp)
    # obtengo el diccionario cuya hora se encuentre más cercana a la actual
    hora_y_temp_cercana = find_closest_datetime(datetime.now(), lista_horas_y_temp)
    logger.info("Hora y temperatura cercana", hora_y_temp_cercana)
    # Si no se encuentra ningun pokemon de acuerdo a la temperatura arroja error
    if hora_y_temp_cercana == "Unknown":
        return "No se pudo obtener la temperatura actual", 404
    # De acuerdo a la temperatura obtenida, devuelvo el tipo de pokemon a buscar
    pokemon_type = get_pokemon_type_by_temp(hora_y_temp_cercana.get("temp"))
    logger.info("Tipo de pokemon a buscar", pokemon_type)
    # Realizo el random de pokemon de acuerdo a su tipo
    random_pokemon = get_random_pokemons_by_letters(pokemon_type)
    return {"pokemon_type": pokemon_type, "random_pokemon": random_pokemon}
