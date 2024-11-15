from flask import jsonify, request
import random
import logging
from apiflask import Schema, APIBlueprint, abort
from apiflask.fields import String, List, Float
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


pokemon_bp = APIBlueprint("pokemon_bp", __name__)
logger = logging.getLogger("pokemon_routes")


class Pokemon(Schema):
    pokemon_name = String()
    pokemon_types = List(String())

class Pokemon_by_temp(Schema):
    lat = Float()
    long = Float()


@pokemon_bp.route("/<name>", methods=["GET"])
@pokemon_bp.output(Pokemon())
@pokemon_bp.doc(responses=[200, 404, 401, 500])
def get_pokemon(name):
    """Se obtiene el tipo de pokemon de acuerdo a su nombre"""
    pokemon_data = get_pokemon_by_name(name)
    if pokemon_data == 404:
        abort(404, message=f"El Pokemon {name} no existe")
    elif pokemon_data == 401:
        abort(401, message="Acceso no autorizado")
    elif pokemon_data == 500:
        abort(500, message="Error interno del servidor")
    else:
        pokemon_types = get_type_by_pokemon(pokemon_data)
        logger.info("Se obtuvo correctamente la información del tipo de pokemon")
        return {"pokemon_types": pokemon_types, "pokemon_name": name}


@pokemon_bp.route("/types/<name>", methods=["GET"])
def get_random_pokemon_by_type(name):
    """De acuerdo al tipo de pokemon colocado en el endpoint, arroja un nombre random de ese mismo tipo"""
    pokemon_data = get_type(name)
    logger.info("Se obtuvo correctamente el listado de pokemones por tipo")
    if pokemon_data == 404:
        return f"El tipo de Pokemon {name} no existe", 404
    elif pokemon_data == 401:
        return "Acceso no autorizado", 401
    elif pokemon_data == 500:
        return "Error interno del servidor", 500
    else:
        pokemon_by_types = get_pokemon_by_types(pokemon_data)
        logger.info("Se obtuvo correctamente la información del pokemon")
        random_value = random.choice(pokemon_by_types)
        return jsonify({"pokemon_name": random_value})


@pokemon_bp.route("/largest_name/<pokemon_type>", methods=["GET"])
def get_largest_name_by_type(pokemon_type):
    """Se obtiene el nombre más largo de pokemon de acuerdo a su tipo especificado en el endpoint"""
    pokemon_data = get_type(pokemon_type)
    if pokemon_data == 404:
        return f"El tipo de Pokemon {pokemon_type} no existe", 404
    elif pokemon_data == 401:
        return "Acceso no autorizado", 401
    elif pokemon_data == 500:
        return "Error interno del servidor", 500
    else:
        pokemon_by_types = get_pokemon_by_types(pokemon_data)
        logger.info("Se obtuvo correctamente el nombre más largo del pokemon")
        return {"pokemon_name": max(pokemon_by_types, key=len)}


@pokemon_bp.route("/random_by_temp", methods=["GET"])
@pokemon_bp.input(Pokemon_by_temp,location="query")
def random_pokemon(query_data):
    lat = query_data.get("lat")
    long = query_data.get("long")
    if not lat or not long:
        return "Falta latitud y longitud", 400
    # guardo diccionario con hora y temperatura agrupada
    hour_y_temp_list = get_hour_temp_from_weather(float(lat), float(long))
    logger.info(
        "Se almacenó correctamente el listado de horas y temperaturas asociadas"
    )
    # obtengo el diccionario cuya hora se encuentre más cercana a la actual
    closest_hour_temp = find_closest_datetime(datetime.now(), hour_y_temp_list)
    logger.info(
        f"Se encontró y almacenó la hora y temperatura cercana y es: {closest_hour_temp.get("hour")}"
    )
    # Si no se encuentra ningun pokemon de acuerdo a la temperatura arroja error
    if closest_hour_temp == "Unknown":
        return "No se pudo obtener la temperatura actual", 404
    # De acuerdo a la temperatura obtenida, devuelvo el tipo de pokemon a buscar
    pokemon_type = get_pokemon_type_by_temp(closest_hour_temp.get("temp"))
    logger.info(f"Tipo de pokemon que debo buscar es: {pokemon_type}")
    # Realizo el random de pokemon de acuerdo a su tipo
    random_pokemon = get_random_pokemons_by_letters(pokemon_type)
    logger.info(
        "Se realizó el random del pokemon de acuerdo a su tipo y letras dentro del nombre"
    )
    return {"pokemon_type": pokemon_type, "random_pokemon": random_pokemon}
