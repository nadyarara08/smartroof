import paho.mqtt.client as mqtt
from config import MQTT_BROKER, TOPIC_CONTROL, TOPIC_MODE
import json

# ===============================
# MQTT CLIENT UNTUK KONTROL
# ===============================
control_client = None

def init_control_client():
    """
    Inisialisasi MQTT client untuk mengirim perintah
    """
    global control_client
    
    if control_client is None:
        control_client = mqtt.Client(client_id="smartroof_controller")
        control_client.connect(MQTT_BROKER, 1883, 60)
        control_client.loop_start()
        print("[CONTROLLER] ✅ MQTT Control Client connected")
    
    return control_client

# ===============================
# KIRIM PERINTAH (BUKA / TUTUP)
# ===============================
def kirim_perintah(aksi: str):
    """
    Mengirim perintah BUKA atau TUTUP ke ESP32
    
    Args:
        aksi: "BUKA" atau "TUTUP"
    """
    client = init_control_client()
    
    # Validasi aksi
    aksi = aksi.upper()
    if aksi not in ["BUKA", "TUTUP"]:
        print(f"[CONTROLLER] ❌ Aksi tidak valid: {aksi}")
        return False
    
    # ✅ PENTING: Format JSON harus sesuai ESP32 (pakai "aksi" bukan "command")
    payload = json.dumps({
        "aksi": aksi,
        "buzzer": 2  # Bunyi 2x
    })
    
    print(f"[CONTROLLER] 📤 Sending to {TOPIC_CONTROL}: {payload}")
    result = client.publish(TOPIC_CONTROL, payload, qos=1)
    
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"[CONTROLLER] ✅ Perintah '{aksi}' dikirim")
        return True
    else:
        print(f"[CONTROLLER] ❌ Gagal mengirim perintah: {result.rc}")
        return False

# ===============================
# UBAH MODE (AUTO / MANUAL)
# ===============================
def ubah_mode(mode: str):
    """
    Mengirim perintah ubah mode ke ESP32
    
    Args:
        mode: "AUTO" atau "MANUAL"
    """
    client = init_control_client()
    
    # Validasi mode
    mode = mode.upper()
    if mode not in ["AUTO", "MANUAL"]:
        print(f"[CONTROLLER] ❌ Mode tidak valid: {mode}")
        return False
    
    # ✅ Format JSON sesuai ESP32
    payload = json.dumps({"mode": mode})
    
    print(f"[CONTROLLER] 📤 Sending to {TOPIC_MODE}: {payload}")
    result = client.publish(TOPIC_MODE, payload, qos=1)
    
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"[CONTROLLER] ✅ Mode '{mode}' dikirim")
        return True
    else:
        print(f"[CONTROLLER] ❌ Gagal mengirim mode: {result.rc}")
        return False

# ===============================
# TESTING
# ===============================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING MQTT CONTROLLER")
    print("="*60)
    
    import time
    
    # Test 1: Kirim perintah BUKA
    print("\n📤 Test 1: Mengirim perintah BUKA")
    kirim_perintah("BUKA")
    time.sleep(3)
    
    # Test 2: Kirim perintah TUTUP
    print("\n📤 Test 2: Mengirim perintah TUTUP")
    kirim_perintah("TUTUP")
    time.sleep(3)
    
    # Test 3: Ubah mode
    print("\n📤 Test 3: Ubah mode ke MANUAL")
    ubah_mode("MANUAL")
    time.sleep(2)
    
    print("\n📤 Test 4: Ubah mode ke AUTO")
    ubah_mode("AUTO")
    
    print("\n" + "="*60)
    print("✅ Testing selesai!")