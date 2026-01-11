import joblib
import pandas as pd
from mqtt_logger import get_latest_data
from config import MODEL_PATH

# =========================
# Load ML model (sekali saja)
# =========================
_bundle = joblib.load(MODEL_PATH)
model = _bundle["model"]
encoder = _bundle["encoder"]

def predict():
    """
    Mengambil data sensor TERAKHIR dari MQTT logger
    dan mengembalikan hasil prediksi ML
    """

    data = get_latest_data()

    # Validasi data
    if data is None:
        return {
            "status": "UNKNOWN",
            "confidence": 0,
            "reason": "Data sensor belum tersedia"
        }

    # =========================
    # Buat DataFrame (1 baris)
    # =========================
    X = pd.DataFrame([{
        "suhu": data["suhu"],
        "kelembapan": data["kelembapan"],
        "cahaya": data["cahaya"],
        "hujan": data["hujan"]
    }])

    # =========================
    # Prediksi
    # =========================
    y_pred = model.predict(X)[0]
    y_prob = model.predict_proba(X).max()

    label = encoder.inverse_transform([y_pred])[0]

    return {
        "status": label.upper(),
        "confidence": round(float(y_prob), 2),
        "source": "ML_DECISION_TREE"
    }
