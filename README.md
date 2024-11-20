Para ejecución local colocar el siguiente comando en la terminal:
flask --app  run.py run --host  0.0.0.0
Para la ejecución desde Docker, colocar los siguientes comandos en la terminal:
docker build -t pokemon_api .
docker run -p 5000:5000 pokemon_api

Para entrar a la documentación: ingresar /docs en la url