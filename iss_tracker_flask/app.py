from flask import Flask, render_template, jsonify, send_from_directory
import urllib.request
import json
import geocoder
import os

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.png', mimetype='image/png')


from flask import Flask, render_template, jsonify
import urllib.request
import json
import geocoder

app = Flask(__name__)


@app.route('/')
def index():
    # Get astronauts data
    astronauts_url = "http://api.open-notify.org/astros.json"
    with urllib.request.urlopen(astronauts_url) as response:
        astronauts_data = json.loads(response.read())

    # Get user location
    try:
        user_location = geocoder.ip('me')
        latlng = user_location.latlng if user_location.ok else None
    except Exception:
        latlng = None

    return render_template('index.html',
                           astronauts=astronauts_data['people'],
                           count=astronauts_data['number'],
                           user_location=latlng)


@app.route('/iss')
def get_iss_position():
    iss_position_url = "http://api.open-notify.org/iss-now.json"
    with urllib.request.urlopen(iss_position_url) as response:
        data = json.loads(response.read())

    position = {
        "latitude": float(data["iss_position"]["latitude"]),
        "longitude": float(data["iss_position"]["longitude"])
    }
    return jsonify(position)

if __name__ == '__main__':
    app.run(debug=True)
