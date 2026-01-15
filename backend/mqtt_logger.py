import json
import csv
import os
from datetime import datetime
from config import CSV_PATH

# ===============================
# GLOBAL STATE
# ===============================
latest_data = None  # ✅ Menyimpan data sensor terakhir

def get_latest_data():
    """
    Return data sensor terakhir yang diterima dari MQTT
    """
    global latest_data
    print(f"[LOGGER] get_latest_data() called, data = {latest_data}")
    return latest_data

# ===============================
# MQTT CALLBACK
# ===============================
def on_message(client, userdata, msg):
    """
    Callback yang dipanggil saat menerima message dari MQTT
    """
    global latest_data
    
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        
        # ✅ Update latest_data
        latest_data = data
        print(f"[MQTT] ✅ Data received: {data}")
        
        # ✅ Log ke CSV
        log_to_csv(data)
        
    except Exception as e:
        print(f"[MQTT ERROR] ❌ {e}")
        import traceback
        traceback.print_exc()

# ===============================
# LOG TO CSV
# ===============================
def log_to_csv(data: dict):
    """
    Menyimpan data ke CSV untuk history
    """
    try:
        # Tambahkan timestamp jika belum ada
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().isoformat()
        
        # Pastikan direktori ada
        csv_dir = os.path.dirname(CSV_PATH)
        if csv_dir and not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
            print(f"[CSV] ✅ Created directory: {csv_dir}")
        
        # Cek apakah file CSV sudah ada
        file_exists = os.path.exists(CSV_PATH)
        
        # Tulis ke CSV
        with open(CSV_PATH, "a", newline="") as f:
            fieldnames = ["timestamp", "suhu", "kelembapan", "cahaya", "hujan"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Tulis header jika file baru
            if not file_exists:
                writer.writeheader()
                print(f"[CSV] ✅ Created new CSV: {CSV_PATH}")
            
            # Tulis data
            writer.writerow({
                "timestamp": data["timestamp"],
                "suhu": data.get("suhu", 0),
                "kelembapan": data.get("kelembapan", 0),
                "cahaya": data.get("cahaya", 0),
                "hujan": data.get("hujan", 0)
            })
            
    except Exception as e:
        print(f"[CSV ERROR] ❌ {e}")
        import traceback
        traceback.print_exc()