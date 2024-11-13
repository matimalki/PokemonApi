from flask import Flask,jsonify,request
from requests import Request, Response
import requests
import random
import logging
from datetime import datetime


app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s %(asctime)s %(message)s')
logger = logging.getLogger(__name__)
#Llamada a la api para consumir lista de pokemones
def get_pokemon_by_name(name: str):
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name}")
    logger.info("Consumiendo Api")
    if response.status_code == 200:
        return response.json()
    else:
        return None
#Llamada a la api para consumir temperatura y hora de acuerdo a coordenadas
def get_weather_by_lat_long(lat: float, lg: float):
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lg}&hourly=temperature_2m&timezone=auto&forecast_days=1")
    logger.info("Consumiendo Api")
    if response.status_code == 200:
        return response.json()
    else:
        return None
#Obtengo lista de tipos de pokemones
def get_type_by_pokemon(pokemon_data):
    pokemon_by_types = pokemon_data.get("types", [])
    logger.info("listado de tipo de pokemones",pokemon_by_types)
    data = []
    for type in pokemon_by_types:
        data.append(type["type"]["name"])
    return data
#Se obtiene el tipo de pokemon de acuerdo al nombre colocado en el endpoint
@app.route("/pokemon/<name>", methods=["GET"])
def get_pokemon(name):
    pokemon_data = get_pokemon_by_name(name)
    if not pokemon_data:
        return f"El Pokemon {name} no existe", 404
    pokemon_types = get_type_by_pokemon(pokemon_data)
    return {"pokemon_types": pokemon_types, "pokemon_name": name}
#Llamada a la api para obtener listado de pokemones de acuerdo al tipo
def get_type(name: str):
    response = requests.get(f"https://pokeapi.co/api/v2/type/{name}")
    logger.info("Consumiendo Api")
    if response.status_code == 200:
        return response.json()
    else:
        return None
#Del listado de los pokemones de acuerdo al tipo se guarda en una lista los nombres de los pokemones
def get_pokemon_by_types(pokemon_data):
    pokemon_types = pokemon_data.get("pokemon", [])
    logger.info("listado de pokemones por tipo", pokemon_types)
    data = []
    for pokemon in pokemon_types:
        data.append(pokemon["pokemon"]["name"])
    return data
#De acuerdo al tipo de pokemon colocado en el endpoint, arroja un nombre random de ese mismo tipo
@app.route("/pokemon_types/<name>", methods=["GET"])    
def get_pokemon_type_random(name):
    pokemon_data = get_type(name)
    if not pokemon_data:
        return f"El tipo de Pokemon {name} no existe", 404
    pokemon_by_types = get_pokemon_by_types(pokemon_data)
    logger.info("tipo de pokemon: ",name,'Listado de pokemones por tipo seleccionado',pokemon_by_types)
    valor_aleatorio = random.choice(pokemon_by_types)
    return jsonify({"pokemon_name": valor_aleatorio})

#Se obtiene el nombre más largo de pokemon de acuerdo a su tipo especificado en el endpoint
@app.route("/largest_name/<name>", methods=["GET"])
def get_largest_name_by_type(name):
    pokemon_data = get_type(name)
    if not pokemon_data:
        return f"El tipo de Pokemon {name} no existe", 404
    pokemon_by_types = get_pokemon_by_types(pokemon_data)
    logger.info("Listado de pokemones por tipo seleccionado",pokemon_by_types)
    return {"pokemon_name": max(pokemon_by_types, key=len)}
#Se genera un nuevo diccionario donde se guardará hora y temperatura relacionada de acuerdo a las coordinadas enviadas
def get_hour_temp_from_weather():
    lat = -34.6131 
    long = -58.3772 
    weather_data = get_weather_by_lat_long(lat, long)
    logger.info(weather_data)
    if not weather_data:
        return f"No se pudo obtener el clima para la latitud {lat} y la longitud {long}", 404
    lista_weather = weather_data.get("hourly")
    logger.info(lista_weather)
    times_weather = lista_weather.get("time")
    logger.info(times_weather)
    temp_weather = lista_weather.get("temperature_2m")
    logger.info(temp_weather)
    hora_temp = []
    logger.info(hora_temp)
    for times, temp in zip(times_weather, temp_weather):
        time_hour_dic = {"hora": datetime.strptime(times, "%Y-%m-%dT%H:%M"), "temp": temp}
        hora_temp.append(time_hour_dic)
    return hora_temp
    

#Funcion para filtrar por letras.
def filter_by_letters(names):
    letras_a_filtrar = {'I','A','M'}
    return [name for name in names if any(char.upper() in letras_a_filtrar for char in name)]   
#Funcion para obtener un pokemon random con letras I, A o M de acuerdo al tipo 
def get_random_pokemons_by_letters(name):
    pokemon_data = get_type(name)
    if not pokemon_data:
        return f"El tipo de Pokemon {name} no existe", 404
    pokemon_by_types = get_pokemon_by_types(pokemon_data)
    logger.info("Listado de pokemones a filtrar",pokemon_by_types)
    filtro_pokemon = filter_by_letters(pokemon_by_types)
    logger.info("Listado de pokemones filtrados",filtro_pokemon)    
    valor_aleatorio = random.choice(filtro_pokemon)
    return valor_aleatorio
   
#Obtengo la fecha más cercana a la actual enviando un diccionario.
def find_closest_datetime(current: datetime, datetimes: list[dict]) -> dict:
    return min(datetimes, key=lambda dt: abs(current - dt.get("hora")))
    
#Obtengo pokemon de acuerdo a la temperatura actual
def get_pokemon_type_by_temp(temperature: float):
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
#Obtengo un random pokemon con I, A o M de acuerdo a la temperatura actual según coordenadas enviadas.
@app.route("/random_pokemon_by_temp", methods=["GET"])
def random_pokemon():
    #guardo diccionario con hora y temperatura agrupada
    lista_horas_y_temp = get_hour_temp_from_weather()
    logger.info("Listado de horas y temp asociadas",lista_horas_y_temp)
    #obtengo el diccionario cuya hora se encuentre más cercana a la actual
    hora_y_temp_cercana = find_closest_datetime(datetime.now(), lista_horas_y_temp)
    logger.info("Hora y temperatura cercana",hora_y_temp_cercana)
    #Si no se encuentra ningun pokemon de acuerdo a la temperatura arroja error
    if hora_y_temp_cercana == "Unknown":
        return "No se pudo obtener la temperatura actual", 404
    #De acuerdo a la temperatura obtenida, devuelvo el tipo de pokemon a buscar
    pokemon_type = get_pokemon_type_by_temp(hora_y_temp_cercana.get("temp"))
    logger.info("Tipo de pokemon a buscar",pokemon_type)
    #Realizo el random de pokemon de acuerdo a su tipo
    random_pokemon = get_random_pokemons_by_letters(pokemon_type)
    return {"pokemon_type": pokemon_type, "random_pokemon": random_pokemon}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
