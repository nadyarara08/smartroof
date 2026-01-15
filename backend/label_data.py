import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "smartroof.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "..", "data", "smartroof_labeled.csv")

# =============================
# Load CSV TANPA HEADER
# =============================
df = pd.read_csv(DATA_PATH, header=None)

# =============================
# Set kolom sesuai data MQTT
# =============================
df.columns = ["timestamp", "suhu", "kelembapan", "cahaya", "hujan"]

# =============================
# Drop timestamp (tidak dipakai ML)
# =============================
df = df.drop(columns=["timestamp"])

# =============================
# Konversi ke numerik (aman)
# =============================
df = df.apply(pd.to_numeric, errors="coerce")

# =============================
# IGNORE DATA ANOMALI
# =============================
df = df[
    (df["suhu"].between(20, 40)) &
    (df["kelembapan"].between(30, 100)) &
    (df["cahaya"].between(0, 4095)) &
    (df["hujan"].isin([0, 1]))
]

# =============================
# LABELING LOGIC (Sesuai aturan kamu)
# =============================
def label_row(row):
    suhu = row["suhu"]
    cahaya = row["cahaya"]
    hujan = row["hujan"]

    if hujan == 1 and cahaya < 200 and suhu <= 25:
        return "hujan"

    if hujan == 0 and cahaya >= 240 and cahaya <= 400 and 25 <= suhu <= 29:
        return "mendung"

    if hujan == 0 and cahaya > 500 and suhu > 29:
        return "cerah"

    return "anomali"

df["label"] = df.apply(label_row, axis=1)

# =============================
# HAPUS BARIS ANOMALI
# =============================
df = df[df["label"] != "anomali"]

# =============================
# SIMPAN
# =============================
df.to_csv(OUTPUT_PATH, index=False)

print("✅ Labeling selesai")
print(df["label"].value_counts())
