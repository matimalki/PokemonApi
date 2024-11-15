import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(asctime)s %(message)s")
logger = logging.getLogger(__name__)


def get_weather_by_lat_long(lat: float, lg: float):
    """Llamada a la api para consumir temperatura y hora de acuerdo a coordenadas"""
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lg}&hourly=temperature_2m&timezone=auto&forecast_days=1"
    )
    if response.status_code == 200:
        logger.info("Se accedió correctamente a la Api")
        return response.json()
    else:
        return None
