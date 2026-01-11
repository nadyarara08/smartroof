import csv
import json
import os
from datetime import datetime
import paho.mqtt.client as mqtt
from config import *

CSV_FILE = CSV_PATH
latest_data = None  # cache data terakhir

def on_message(client, userdata, msg):
    print("DATA MASUK:", msg.payload.decode())

    global latest_data
    data = json.loads(msg.payload.decode())
    latest_data = data

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now(),
            data["suhu"],
            data["kelembapan"],
            data["cahaya"],
            data["hujan"]
        ])

def get_latest_data():
    return latest_data

client = mqtt.Client()
client.connect(MQTT_BROKER, 1883)
client.subscribe(TOPIC_SENSOR)
client.on_message = on_message

print("MQTT Logger berjalan...")
client.loop_forever()
