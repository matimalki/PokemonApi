from flask import Flask
from requests import Request, Response
import requests

app = Flask(__name__)

def get_pokemon_by_name(name: str):
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name}")
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
def get_pokemon_type(name):
    pokemon_data = get_type(name)
    if not pokemon_data:
        return f"El tipo de Pokemon {name} no existe", 404
    pokemon_by_types = get_pokemon_by_types(pokemon_data)
    return {"pokemon_by_types": pokemon_by_types, "pokemon_type": name}
#Busco todos los pokemones existentes por tipo   
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
