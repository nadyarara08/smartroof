import streamlit as st
import pandas as pd
from ai_predictor import *

st.set_page_config(page_title="Smart Roof Admin", layout="wide")

st.title("📊 SMART ROOF ADMIN DASHBOARD")

df = pd.read_csv("../backend/data/smartroof.csv")

st.subheader("Data Sensor Terakhir")
st.write(df.tail(1))

st.subheader("Prediksi AI")
pred = predict()
st.json(pred)

st.subheader("Grafik Suhu")
st.line_chart(df["suhu"])

st.subheader("Grafik Kelembapan")
st.line_chart(df["kelembapan"])

st.subheader("Grafik Cahaya")
st.line_chart(df["cahaya"])
