from flask import Flask,jsonify,request
from requests import Request, Response
import requests
import random
from datetime import datetime


app = Flask(__name__)

def get_pokemon_by_name(name: str):
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name}")
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_weather_by_lat_long(lat: float, lg: float):
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lg}&hourly=temperature_2m&timezone=auto&forecast_days=1")
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_pokemon_by_type(pokemon_data):
   #types = [type["type"]["name"] for type in pokemon_data["types"]]
    #return types
    pokemon_by_types = pokemon_data.get("types", [])
    data = []
    for type in pokemon_by_types:
        data.append(type["type"]["name"])
    return data

@app.route("/pokemon/<name>", methods=["GET"])
def get_pokemon(name):
    pokemon_data = get_pokemon_by_name(name)
    if not pokemon_data:
        return f"El Pokemon {name} no existe", 404
    pokemon_types = get_pokemon_by_type(pokemon_data)
    return {"pokemon_types": pokemon_types, "pokemon_name": name}

def get_type(name: str):
    response = requests.get(f"https://pokeapi.co/api/v2/type/{name}")
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_pokemon_by_types(pokemon_data):
   #types = [type["type"]["name"] for type in pokemon_data["types"]]
    #return types
    pokemon_types = pokemon_data.get("pokemon", [])
    data = []
    for pokemon in pokemon_types:
        data.append(pokemon["pokemon"]["name"])
    return data
@app.route("/pokemon_types/<name>", methods=["GET"])    
def get_pokemon_type_random(name):
    ##name = request.args.get('hola') pasar como parametros a la url
    pokemon_data = get_type(name)
    if not pokemon_data:
        return f"El tipo de Pokemon {name} no existe", 404
    pokemon_by_types = get_pokemon_by_types(pokemon_data)
    valor_aleatorio = random.choice(pokemon_by_types)
    return jsonify({"pokemon_name": valor_aleatorio})


@app.route("/largest_name/<name>", methods=["GET"])
def get_largest_name(name):
    pokemon_data = get_type(name)
    if not pokemon_data:
        return f"El tipo de Pokemon {name} no existe", 404
    pokemon_by_types = get_pokemon_by_types(pokemon_data)
    return {"pokemon_name": max(pokemon_by_types, key=len)}

def get_hour():
    lat = -34.6131 #float(request.args.get('lat'))
    long = -58.3772 #float(request.args.get('long'))
    weather_data = get_weather_by_lat_long(lat, long)
    if not weather_data:
        return f"No se pudo obtener el clima para la latitud {lat} y la longitud {long}", 404
    lista_weather = weather_data.get("hourly")
    times_weather = lista_weather.get("time")
    temp_weather = lista_weather.get("temperature_2m")
    hora_temp = []
    for times, temp in zip(times_weather, temp_weather):
        diccionario_nuevo = {"hora": datetime.strptime(times, "%Y-%m-%dT%H:%M"), "temp": temp}
        hora_temp.append(diccionario_nuevo)
    return hora_temp

def filter_iam(names):
    letras_a_filtrar = {'I','A','M'}
    return [name for name in names if any(char.upper() in letras_a_filtrar for char in name)]  
    # for name in names:  
        # if any(char.upper() in letras_a_filtrar for char in name):
        #     names.remove(name)
        #     break  # para que no siga buscando en los demás nombres si ya lo ha encontrado  
def get_random_pokemons(name):
    pokemon_data = get_type(name)
    if not pokemon_data:
        return f"El tipo de Pokemon {name} no existe", 404
    pokemon_by_types = get_pokemon_by_types(pokemon_data)
    filtro_pokemon = filter_iam(pokemon_by_types)    
    valor_aleatorio = random.choice(filtro_pokemon)
    return valor_aleatorio
   

def find_closest_datetime(current: datetime, datetimes: list[dict]) -> dict:
    return min(datetimes, key=lambda dt: abs(current - dt.get("hora")))
    

#def hora_actual():
 #   lista_horas_y_temp = get_hour() 
  #  hora_y_temp_cercana = find_closest_datetime(datetime.now(), lista_horas_y_temp)   
   # return hora_y_temp_cercana
def getpokemon_type(temperature: float):
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
@app.route("/random_pokemon_by_temp", methods=["GET"])
def random_poke_type():
    lista_horas_y_temp = get_hour() 
    hora_y_temp_cercana = find_closest_datetime(datetime.now(), lista_horas_y_temp)
    if hora_y_temp_cercana == "Unknown":
        return "No se pudo obtener la temperatura actual", 404
    pokemon_type = getpokemon_type(hora_y_temp_cercana.get("temp"))
    random_pokemon = get_random_pokemons(pokemon_type)
    return {"pokemon_type": pokemon_type, "random_pokemon": random_pokemon}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
