import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "smartroof.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "..", "data", "smartroof_labeled.csv")

df = pd.read_csv(DATA_PATH)

def label_row(row):
    if row["suhu"] <= 27:
        return "hujan"
    elif row["suhu"] < 29:
        return "mendung"
    else:
        return "cerah"

df["label"] = df.apply(label_row, axis=1)

df.to_csv(OUTPUT_PATH, index=False)

print("Labeling selesai berdasarkan SUHU")
print(df["label"].value_counts())
