from ai_predictor import predict
from notifier import notify

def ai_warning():
    prediksi = predict()

    if prediksi["status"] == "HUJAN":
        notify(
            f"⚠️ PERINGATAN AI: Potensi HUJAN "
            f"(confidence {prediksi['confidence']})"
        )
        return "AI_WARNING_SENT"

    return "AI_NO_WARNING"
