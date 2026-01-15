import joblib
import pandas as pd
import os
from mqtt_logger import get_latest_data  # ✅ FIX: Import dari mqtt_logger
from config import MODEL_PATH

# ===============================
# LOAD MODEL
# ===============================
model = None
model_loaded = False

try:
    if os.path.exists(MODEL_PATH):
        print(f"[AI] Loading model from: {MODEL_PATH}")
        model = joblib.load(MODEL_PATH)
        model_loaded = True
        print("[AI] ✅ Model loaded successfully")
    else:
        print(f"[AI] ⚠️ Model file not found: {MODEL_PATH}")
except Exception as e:
    print(f"[AI] ❌ Error loading model: {e}")


# ===============================
# MODEL INFO
# ===============================
def get_model_info():
    """Return informasi model"""
    if model_loaded:
        return {
            "loaded": True,
            "type": "Decision Tree",
            "status": "ready",
            "model_path": MODEL_PATH,
            "features": ["suhu", "kelembapan", "cahaya", "hujan"]
        }
    else:
        return {
            "loaded": False,
            "type": "Unknown",
            "status": "Model tidak ditemukan atau gagal dimuat",
            "model_path": MODEL_PATH
        }


# ===============================
# NORMALIZE DATA
# ===============================
def normalize_data(data: dict):
    """
    Menyamakan key data dari MQTT → format ML
    """
    return {
        "suhu": float(data.get("suhu", 0) or 0),
        "kelembapan": float(data.get("kelembapan", 0) or 0),
        "cahaya": int(data.get("cahaya", 0) or 0),
        "hujan": int(data.get("hujan", 0) or 0),
    }


# ===============================
# PREDICT
# ===============================
def predict():
    """
    Prediksi cuaca berdasarkan data sensor terakhir
    
    Returns:
        dict: {
            "status": "CERAH|MENDUNG|HUJAN|ERROR|NO_DATA",
            "confidence": float (0-1),
            "source": "DECISION_TREE",
            "reason": str (optional)
        }
    """
    try:
        # Cek model
        if not model_loaded or model is None:
            print("[AI] Model belum dimuat")
            return {
                "status": "ERROR",
                "confidence": 0,
                "reason": "Model AI belum dimuat",
                "source": "SYSTEM"
            }

        # Ambil data sensor
        raw_data = get_latest_data()
        print(f"[AI] Raw data dari sensor: {raw_data}")  # ✅ DEBUG

        if raw_data is None:
            print("[AI] Data sensor = None")
            return {
                "status": "NO_DATA",
                "confidence": 0,
                "reason": "Data sensor belum tersedia",
                "source": "SYSTEM"
            }

        # Normalize data
        data = normalize_data(raw_data)
        print(f"[AI] Normalized data: {data}")  # ✅ DEBUG

        # Validasi data
        if data["suhu"] == 0 and data["kelembapan"] == 0:
            print("[AI] Data tidak valid (semua 0)")
            return {
                "status": "INVALID",
                "confidence": 0,
                "reason": "Data sensor tidak valid (semua nilai 0)",
                "source": "SYSTEM"
            }

        # Buat DataFrame untuk prediksi
        X = pd.DataFrame([data])
        print(f"[AI] DataFrame untuk prediksi:\n{X}")  # ✅ DEBUG

        # Prediksi
        pred = model.predict(X)[0]
        print(f"[AI] Prediction: {pred}")  # ✅ DEBUG

        # Confidence (jika model support probability)
        confidence = 1.0
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)[0]
            confidence = max(proba)
            print(f"[AI] Confidence: {confidence}")  # ✅ DEBUG

        # Return hasil
        result = {
            "status": str(pred).upper(),
            "confidence": round(float(confidence), 2),
            "source": "DECISION_TREE",
            "sensor_data": data
        }
        print(f"[AI] Final result: {result}")  # ✅ DEBUG
        return result

    except Exception as e:
        print(f"[AI ERROR] {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "status": "ERROR",
            "confidence": 0,
            "reason": str(e),
            "source": "EXCEPTION"
        }


# ===============================
# TESTING
# ===============================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING AI PREDICTOR")
    print("="*60)
    
    # Test 1: Model info
    info = get_model_info()
    print("\n📊 Model Info:")
    for k, v in info.items():
        print(f"   {k}: {v}")
    
    # Test 2: Prediction
    print("\n🔮 Running prediction...")
    result = predict()
    print("\n📈 Prediction Result:")
    for k, v in result.items():
        print(f"   {k}: {v}")
    
    print("\n" + "="*60)