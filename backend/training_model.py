import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Load dataset berlabel
df = pd.read_csv("../data/smartroof_labeled.csv")

# ===== FEATURE & LABEL =====
X = df[["suhu", "kelembapan", "hujan"]]   # LDR boleh dihapus dulu
y = df["label"]

# ===== SPLIT DATA =====
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ===== TRAIN MODEL =====
model = DecisionTreeClassifier(max_depth=5)
model.fit(X_train, y_train)

# ===== EVALUASI =====
y_pred = model.predict(X_test)
print("\nHasil Evaluasi Model:")
print(classification_report(y_test, y_pred))

# ===== SIMPAN MODEL =====
joblib.dump(model, "../model/smartroof_model.pkl")
print("\nModel berhasil disimpan!")
