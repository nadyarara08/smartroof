import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(BASE_DIR, "..", "data", "smartroof_labeled.csv")
MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "smartroof_model.pkl")

print("\n" + "="*60)
print("🤖 TRAINING SMART ROOF MODEL (4 Features)")
print("="*60)

# =========================
# LOAD DATA
# =========================
print("\n📂 Loading data...")
df = pd.read_csv(DATA_PATH)

print(f"✅ Data loaded: {len(df)} rows")
print(f"📊 Columns: {list(df.columns)}")

# Cek apakah kolom 'hujan' ada
if 'hujan' not in df.columns:
    print("\n⚠️ WARNING: Kolom 'hujan' tidak ada di dataset!")
    print("   Menambahkan kolom 'hujan' dengan nilai default 0...")
    df['hujan'] = 0

# =========================
# FEATURE & LABEL
# =========================
# ✅ GUNAKAN 4 FITUR (termasuk hujan)
feature_columns = ["suhu", "kelembapan", "cahaya", "hujan"]
X = df[feature_columns]
y = df["label"]

print(f"\n📊 Features: {feature_columns}")
print(f"🎯 Target column: 'label'")
print(f"   Classes: {list(y.unique())}")
print(f"   Distribution:")
for cls in y.unique():
    count = (y == cls).sum()
    pct = (count / len(y)) * 100
    print(f"      - {cls}: {count} ({pct:.1f}%)")

# =========================
# SPLIT DATA
# =========================
print("\n📦 Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"   Train set: {len(X_train)} rows")
print(f"   Test set: {len(X_test)} rows")

# =========================
# TRAIN MODEL
# =========================
print("\n🎓 Training Decision Tree model...")
model = DecisionTreeClassifier(
    max_depth=5,
    min_samples_split=10,  # Cegah overfitting
    class_weight={
        "mendung": 1.5,  # Prioritas early warning
        "hujan": 1.2,
        "cerah": 1.0
    },
    random_state=42
)

model.fit(X_train, y_train)
print("✅ Training complete!")

# =========================
# EVALUASI
# =========================
print("\n📈 Evaluating model...")
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n✅ Accuracy: {accuracy:.2%}")
print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred))

# Feature importance
print("\n🔍 Feature Importance:")
for feature, importance in zip(feature_columns, model.feature_importances_):
    print(f"   {feature:15s}: {importance:.4f} ({importance*100:.1f}%)")

# =========================
# SIMPAN MODEL
# =========================
print(f"\n💾 Saving model to: {MODEL_PATH}")
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(model, MODEL_PATH)
print("✅ Model saved successfully!")

# =========================
# VERIFY MODEL
# =========================
print("\n🔍 Verifying saved model...")
loaded_model = joblib.load(MODEL_PATH)

# Cek feature names
if hasattr(loaded_model, 'feature_names_in_'):
    print(f"✅ Feature names in model: {list(loaded_model.feature_names_in_)}")
else:
    print("⚠️ Model doesn't store feature names (sklearn < 1.0)")

# Test prediction
print("\n🧪 Testing prediction with sample data...")
test_data = pd.DataFrame([{
    "suhu": 28.0,
    "kelembapan": 80.0,
    "cahaya": 150,
    "hujan": 0
}])

try:
    test_pred = loaded_model.predict(test_data)
    print(f"✅ Test prediction: {test_pred[0]}")
    
    if hasattr(loaded_model, 'predict_proba'):
        proba = loaded_model.predict_proba(test_data)[0]
        print(f"   Confidence: {max(proba):.2%}")
        print(f"   Probabilities:")
        for cls, prob in zip(loaded_model.classes_, proba):
            print(f"      - {cls}: {prob:.2%}")
except Exception as e:
    print(f"❌ Test prediction failed: {e}")

print("\n" + "="*60)
print("✅ TRAINING COMPLETE!")
print("="*60)
print(f"\nModel saved to: {MODEL_PATH}")
print("Run: python ai_predictor.py (untuk test)")
print("="*60)