import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

API_KEY = ""
ACCESS_KEY = ""

app = Flask(__name__)


def get_weather(city: str, date: str):
    url_base_url = "https://api.weatherapi.com/v1"
    url_api = "history.json"

    url = f"{url_base_url}/{url_api}?key={API_KEY}&q={city}&dt={date}"

    response = requests.request("GET", url)
    return json.loads(response.text)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA Lab1: Python Saas.</h2></p>"


@app.route(
    "/content/api/v1/integration/generate",
    methods=["POST"],
)
def joke_endpoint():
    start_dt = dt.datetime.now()
    json_data = request.get_json()

    if json_data.get("requester_name") is None:
        raise InvalidUsage("requester_name is required", status_code=400)

    name = json_data.get("requester_name")

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if json_data.get("city") is None:
        raise InvalidUsage("city is required", status_code=400)

    city = json_data.get("city")

    if json_data.get("date") is None:
        raise InvalidUsage("date is required", status_code=400)

    date = json_data.get("date")

    if token != ACCESS_KEY:
        raise InvalidUsage("wrong access key", status_code=403)

    weather_response = get_weather(city, date)
    weather_stats = weather_response['forecast']['forecastday'][0]

    weather = {
        "temp_c": weather_stats['day']['avgtemp_c'],
        "wind_kph": weather_stats['day']['maxwind_kph'],
        "pressure_mb": weather_stats['hour'][0]['pressure_mb'],
        "humidity": weather_stats['day']['avghumidity'],
    }

    result = {
        "location": weather_response['location']['name'],
        "requester_name": name,
        "timestamp": start_dt.isoformat(),
        "weather": weather,
    }

    return result
