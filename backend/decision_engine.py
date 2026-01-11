import time
from mqtt_logger import get_latest_data
from mqtt_controller import kirim_perintah
from ai_warning import ai_warning

FAILSAFE_TIMEOUT = 5  # detik (simulasi), real: 300

last_manual_time = None

def decision_engine(mode):
    global last_manual_time

    data = get_latest_data()
    if data is None:
        return "DATA TIDAK TERSEDIA"

    # =========================
    # 1. SENSOR HUJAN PRIORITAS
    # =========================
    if data["hujan"] == 1:
        kirim_perintah("TUTUP", "FAILSAFE")
        return "HUJAN TERDETEKSI - ATAP DITUTUP"

    # =========================
    # 2. MODE MANUAL
    # =========================
    if mode == "MANUAL":
        if last_manual_time is None:
            last_manual_time = time.time()
            return "MODE MANUAL - MENUNGGU AKSI USER"

        # FAILSAFE JIKA USER DIAM
        if time.time() - last_manual_time > FAILSAFE_TIMEOUT:
            kirim_perintah("TUTUP", "TIMEOUT")
            last_manual_time = None
            return "TIMEOUT - ATAP DITUTUP OTOMATIS"

        return "MODE MANUAL AKTIF"

    # =========================
    # 3. MODE AUTO
    # =========================
    if mode == "AUTO":
        ai_warning()
        return "MODE AUTO - MONITORING"

    return "STATUS TIDAK DIKENAL"
