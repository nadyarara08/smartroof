# Smart Sliding Roof IoT Dashboard 🌤️🏠

Smart Sliding Roof adalah sebuah aplikasi web dashboard berbasis IoT yang digunakan untuk memonitor kondisi lingkungan dan mengontrol sistem atap geser pintar (smart sliding roof). Dashboard ini menampilkan data sensor secara real-time serta memberikan kontrol terhadap status buka/tutup atap berdasarkan kondisi cuaca.

## 📌 Overview

Project ini merupakan simulasi antarmuka sistem IoT untuk smart roof yang dapat membantu pengguna memantau:

- Suhu lingkungan
- Kelembapan udara
- Intensitas cahaya
- Kondisi cuaca
- Status atap (terbuka/tertutup)
- Notifikasi perubahan kondisi

Dashboard dibuat dengan tampilan modern menggunakan konsep **glassmorphism UI** agar terlihat seperti aplikasi monitoring IoT profesional.

## ✨ Features

### 🌡️ Monitoring Sensor
Menampilkan data sensor:
- Temperature (°C)
- Humidity (%)
- Light intensity (Lux)
- Weather condition

### ☀️ Weather Simulation
Dashboard dapat menampilkan kondisi cuaca:
- Cerah
- Mendung
- Hujan

Background dan tampilan dashboard akan menyesuaikan kondisi cuaca.

### 🏠 Smart Roof Control
Kontrol sistem atap:
- Membuka atap
- Menutup atap
- Menampilkan status posisi atap

### 🔔 Notification System
Sistem notifikasi untuk memberi informasi perubahan kondisi seperti:
- Perubahan cuaca
- Perubahan status atap
- Update sensor

### ⏰ Real-time Clock
Menampilkan waktu secara real-time pada dashboard.

---

## 🛠️ Technologies Used

Project ini dibuat menggunakan:

- HTML5
- CSS3
- JavaScript (Vanilla JS)
- SVG Icons
- Responsive Web Design

---

## 📂 Project Structure

SmartRoof-WebApp/
│
├── main.html # Halaman utama dashboard
├── style.css # Styling dan tampilan UI
└── script.js # Logic aplikasi dan simulasi IoT

---

## 🚀 How To Run

1. Clone repository, git clone https://github.com/username/SmartRoof-WebApp.git

2. Masuk ke folder project
cd SmartRoof-WebApp
Jalankan file:
main.html

## ⚙️ Cara Kerja Sistem

Saat aplikasi dijalankan, sistem melakukan inisialisasi data sensor.
JavaScript membaca nilai sensor (simulasi).
Data ditampilkan ke dashboard.
Kondisi cuaca akan mempengaruhi tampilan dashboard.
Pengguna dapat mengubah status atap melalui kontrol yang tersedia.
Sistem memberikan notifikasi berdasarkan perubahan kondisi.
