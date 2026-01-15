import pandas as pd
import os
from config import CSV_PATH

def get_latest_data():
    """
    Ambil data sensor terakhir dari CSV
    
    Returns:
        dict | None: {suhu, kelembapan, cahaya, hujan, roof}
    """
    try:
        # Cek file exist
        if not os.path.exists(CSV_PATH):
            print(f"[DATA_READER] ⚠️ File tidak ditemukan: {CSV_PATH}")
            return None

        # Baca CSV
        df = pd.read_csv(CSV_PATH)

        if df.empty:
            print("[DATA_READER] ⚠️ CSV kosong")
            return None

        # Ambil baris terakhir
        latest = df.iloc[-1].to_dict()

        # Format output
        result = {
            "suhu": float(latest.get("suhu", 0)),
            "kelembapan": float(latest.get("kelembapan", 0)),
            "cahaya": int(latest.get("cahaya", 0)),
            "hujan": int(latest.get("hujan", 0)),
            "roof": str(latest.get("roof", "CLOSED")).upper()
        }

        print(f"[DATA_READER] ✅ Data: T={result['suhu']}°C, H={result['kelembapan']}%, L={result['cahaya']}, R={result['hujan']}, Roof={result['roof']}")
        
        return result

    except Exception as e:
        print(f"[DATA_READER ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None


# ===============================
# TESTING
# ===============================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING DATA READER")
    print("="*60)
    
    data = get_latest_data()
    
    if data:
        print("\n✅ Data berhasil dibaca:")
        for k, v in data.items():
            print(f"   {k}: {v}")
    else:
        print("\n❌ Gagal membaca data")
    
    print("\n" + "="*60)