#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from flask import Flask, render_template, jsonify
from flask_mqtt import Mqtt
import folium

app = Flask(__name__)

# MQTT configuration (public HiveMQ)
app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TLS_ENABLED'] = False

mqtt = Mqtt(app)

# All team positions
teams = {}


# Start page
@app.route('/')
def index():
    fmap = folium.Map(location=[48.5, 14.4], zoom_start=8)
    map_html = fmap.get_root().render()
    return render_template('index.html', map_html=map_html)


# API current team positions
@app.route('/positions')
def get_positions():
    return jsonify(teams)


# MQTT connected
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("connected, rc:", rc)
    mqtt.subscribe("radiocaching/ff/search_teams/+/coordinates")


# MQTT received message
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    try:
        topic_parts = message.topic.split('/')
        vid = topic_parts[1]

        # parse from json
        data = json.loads(message.payload.decode())

        lat = data['latitude']
        lon = data['longitude']
        teams[vid] = (lat, lon)
        print(f"Update: {vid} -> {lat}, {lon}")
    except Exception as e:
        print("Error on MQTT receive:", e)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
