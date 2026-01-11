import os
import firebase_admin
from firebase_admin import credentials, db
from mqtt_controller import kirim_perintah
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "firebase_key.json")

cred = credentials.Certificate(KEY_PATH)

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://smartroof-fourty-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

ref = db.reference("smartroof")

last_cmd_time = time.time()

def listen():
    global last_cmd_time
    while True:
        data = ref.get()

        if data["mode"] == "MANUAL":
            cmd = data["command"]
            if cmd in ["BUKA", "TUTUP"]:
                kirim_perintah(cmd, "MANUAL")
                last_cmd_time = time.time()
                ref.update({"command": "NONE"})

        time.sleep(1)

listen()
