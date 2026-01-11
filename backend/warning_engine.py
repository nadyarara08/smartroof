from notifier import notify

def generate_warning(pred5, pred10):
    if pred5["status"] == "HUJAN":
        notify(
            f"⚠️ Peringatan: Potensi hujan dalam 5 menit "
            f"(confidence {pred5['probabilitas']})"
        )
        return pred5

    if pred10["status"] == "HUJAN":
        notify(
            f"⚠️ Peringatan: Potensi hujan dalam 10 menit "
            f"(confidence {pred10['probabilitas']})"
        )
        return pred10

    return {"status": "AMAN"}
