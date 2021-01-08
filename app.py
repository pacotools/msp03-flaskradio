import os
import requests
from flask import (Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

@app.route("/", methods=["GET", "POST"])
def home():
    url = "https://freegeoip.app/json/"
    headers = {
        'accept': "application/json",
        'content-type': "application/json"
    }
    response = requests.request("GET", url, headers=headers)
    session['country_name'] = response.json()["country_name"]
    session['current_station'] = str(mongo.db.stations.find_one({'country': session['country_name']})['_id'])
    session['user'] = ""
    return redirect(url_for('radio'))


@app.route("/radio", methods=["GET", "POST"])
def radio():
    countries = list(mongo.db.countries.find().sort("name", 1))
    stations = list(mongo.db.stations.find({'country': session['country_name']}))
    favorites = list(mongo.db.favorites.find({'user': session['user'].lower()}))

    station_info = {
        "country_name": stations[0]['country'],
        "station_id": stations[0]['_id'],
        "url_resolved": stations[0]['url_resolved'],
        "station_name": stations[0]['name'],
        "homepage": stations[0]['homepage'],
        "favicon": stations[0]['favicon'],
        "tags": stations[0]['tags'],
    }
    return render_template("radio.html", station_info=station_info, countries=countries,
                            stations=stations, favorites=favorites)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
