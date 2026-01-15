import streamlit as st
import pandas as pd
import os
import sys

# TAMBAHKAN PATH BACKEND SECARA EKSPLISIT
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

# SEKARANG IMPORT LANGSUNG (TANPA "backend.")
from backend.ai_predictor import predict

st.set_page_config(page_title="Smart Roof Admin", layout="wide")

st.title("📊 SMART ROOF ADMIN DASHBOARD")

# Perbaiki path CSV
csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'smartroof.csv')

try:
    df = pd.read_csv(csv_path)
    
    st.subheader("Data Sensor Terakhir")
    st.write(df.tail(1))
    
    st.subheader("Grafik Suhu")
    st.line_chart(df["suhu"])
    
    st.subheader("Grafik Kelembapan")
    st.line_chart(df["kelembapan"])
    
    st.subheader("Grafik Cahaya")
    st.line_chart(df["cahaya"])
    
except FileNotFoundError:
    st.error(f"File CSV tidak ditemukan di: {csv_path}")

st.subheader("Prediksi AI")
try:
    pred = predict()
    st.json(pred)
except Exception as e:
    st.error(f"Error saat prediksi: {str(e)}")