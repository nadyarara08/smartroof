from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import List, Dict
import csv
import os

# ===============================
# INTERNAL IMPORT
# ===============================
from mqtt_logger import get_latest_data
from mqtt_service import start_mqtt_thread
from ai_predictor import predict, get_model_info
from mqtt_controller import kirim_perintah, ubah_mode
from config import CSV_PATH

# ===============================
# GLOBAL STATE
# ===============================
notifications: List[Dict] = []
current_mode = "AUTO"

def add_notification(message: str, notif_type: str = "default"):
    notifications.insert(0, {
        "time": datetime.now().strftime("%H:%M:%S"),
        "message": message,
        "type": notif_type,
        "timestamp": datetime.now().isoformat()
    })
    if len(notifications) > 100:
        notifications.pop()

# ===============================
# HISTORICAL DATA
# ===============================
def get_historical_data(hours: int = 24) -> List[Dict]:
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        data = []

        if not os.path.exists(CSV_PATH):
            return []

        with open(CSV_PATH, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    row_time = datetime.fromisoformat(row["timestamp"])
                    if row_time >= cutoff_time:
                        data.append({
                            "time": row_time.strftime("%H:%M"),
                            "suhu": float(row["suhu"]),
                            "kelembapan": float(row["kelembapan"]),
                            "cahaya": int(row["cahaya"]),
                            "hujan": int(row["hujan"])
                        })
                except Exception:
                    continue

        if len(data) > 144:
            step = len(data) // 144
            data = data[::step]

        return data
    except Exception as e:
        print("[HISTORY ERROR]", e)
        return []

# ===============================
# AI MONITORING STATE
# ===============================
last_rain_sensor = 0
last_ai_status = None
ai_predictions_log = []

# ===============================
# FASTAPI APP
# ===============================
app = FastAPI(
    title="Smart Roof Web App",
    description="IoT Monitoring & Control System with AI Weather Prediction",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(BASE_DIR, "web-app")

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(WEB_DIR, "static")),
    name="static"
)

templates = Jinja2Templates(
    directory=os.path.join(WEB_DIR, "templates")
)

# ===============================
# ROUTES
# ===============================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/manifest.json")
def manifest():
    import json
    with open("static/manifest.json") as f:
        return json.load(f)

@app.get("/api/sensor")
def api_sensor():
    global last_rain_sensor

    data = get_latest_data()
    if data is None:
        return {"error": "no_data"}

    if data["hujan"] == 1 and last_rain_sensor == 0:
        add_notification("🌧️ HUJAN TERDETEKSI! Atap ditutup otomatis.", "danger")

    last_rain_sensor = data["hujan"]
    return data

@app.get("/api/predict")
def api_predict():
    global last_ai_status

    result = predict()

    ai_predictions_log.insert(0, {
        "timestamp": datetime.now().isoformat(),
        "prediction": result
    })
    ai_predictions_log[:] = ai_predictions_log[:50]

    if result.get("status") == "HUJAN" and result.get("confidence", 0) >= 0.7:
        key = f"{result['status']}-{int(result['confidence'] * 10)}"
        if last_ai_status != key:
            add_notification(
                f"⚠️ AI Prediksi hujan ({int(result['confidence']*100)}%)",
                "warning"
            )
            last_ai_status = key
    else:
        last_ai_status = None

    return result

@app.get("/api/history/{hours}h")
def api_history(hours: int = 24):
    hours = min(max(1, hours), 168)
    history = get_historical_data(hours)
    return {"history": history, "count": len(history)}

@app.get("/api/notifications")
def api_notifications():
    return {"notifications": notifications}

@app.get("/api/mode")
def api_get_mode():
    return {"mode": current_mode}

@app.post("/api/mode/{mode}")
def api_set_mode(mode: str):
    global current_mode
    mode = mode.upper()

    if mode not in ["AUTO", "MANUAL"]:
        return JSONResponse(status_code=400, content={"error": "invalid_mode"})

    ubah_mode(mode)
    current_mode = mode
    add_notification(f"🤖 Mode diubah ke {mode}", "info")

    return {"status": "success", "mode": mode}

@app.post("/api/control/{aksi}")
def api_control(aksi: str):
    aksi = aksi.upper()
    if aksi not in ["BUKA", "TUTUP"]:
        return JSONResponse(status_code=400, content={"error": "invalid_action"})

    kirim_perintah(aksi)
    add_notification(f"🎮 Perintah {aksi} dikirim", "info")

    return {"status": "success", "action": aksi}

@app.get("/api/health")
def api_health():
    return {
        "mqtt": get_latest_data() is not None,
        "ai_loaded": get_model_info().get("loaded"),
        "mode": current_mode,
        "time": datetime.now().isoformat()
    }

# ===============================
# STARTUP
# ===============================
@app.on_event("startup")
async def startup_event():
    print("🏠 SMART ROOF BACKEND STARTED")
    start_mqtt_thread()
    add_notification("✅ Sistem Smart Roof aktif", "success")
