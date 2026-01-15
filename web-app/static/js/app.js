// ============================================
// SMART ROOF WEB APP - FIXED WITH MODE CONTROL
// ============================================

const API_BASE = "https://subcivilized-nonmortally-shad.ngrok-free.dev";
const POLL_INTERVAL = 3000; // 3 detik
const AI_CHECK_INTERVAL = 60000; // 60 detik
const WEATHER_ICONS = {
  CERAH: "☀️",
  MENDUNG: "☁️",
  HUJAN: "🌧️"
};

let pollTimer = null;
let aiCheckTimer = null;
let isLoading = false;
let sensorChart = null;
let currentChartType = "temp";
let lastRainWarning = 0;
let lastAIWarning = 0;
let lastAIPrediction = null;
let currentMode = "AUTO"; // ✅ NEW: Track current mode

// ============================================
// PUSH NOTIFICATION SETUP
// ============================================
async function requestNotificationPermission() {
  if (!("Notification" in window)) {
    console.warn("Browser tidak support notifikasi");
    return false;
  }

  if (Notification.permission === "granted") {
    return true;
  }

  if (Notification.permission !== "denied") {
    const permission = await Notification.requestPermission();
    return permission === "granted";
  }

  return false;
}

function showPushNotification(title, options = {}) {
  if (Notification.permission === "granted") {
    const notification = new Notification(title, {
      icon: "/static/icons/icon-192.png",
      badge: "/static/icons/icon-72.png",
      vibrate: [200, 100, 200],
      ...options
    });

    notification.onclick = () => {
      window.focus();
      notification.close();
    };

    setTimeout(() => notification.close(), 10000);
  }
}

// ============================================
// UTILITY: Clock
// ============================================
function updateClock() {
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');
  document.getElementById("time").textContent = `${hours}.${minutes}.${seconds}`;
}

// ============================================
// UTILITY: Show/Hide Loading
// ============================================
function showLoading() {
  isLoading = true;
  document.getElementById("loading").style.display = "flex";
}

function hideLoading() {
  isLoading = false;
  document.getElementById("loading").style.display = "none";
}

// ============================================
// UTILITY: Update Connection Status
// ============================================
function updateConnectionStatus(connected) {
  const statusEl = document.getElementById("connection-status");
  if (connected) {
    statusEl.className = "connected";
    statusEl.textContent = "● Connected";
  } else {
    statusEl.className = "disconnected";
    statusEl.textContent = "● Disconnected";
  }
}

// ============================================
// SENSOR: Get Status Text
// ============================================
function getTempStatus(temp) {
  if (temp < 20) return "Dingin";
  if (temp < 28) return "Sejuk";
  if (temp < 32) return "Hangat";
  return "Panas";
}

function getHumStatus(hum) {
  if (hum < 40) return "Kering";
  if (hum < 70) return "Lembap";
  return "Sangat Lembap";
}

function getLightStatus(light) {
  if (light < 300) return "Gelap";
  if (light < 700) return "Redup";
  return "Terang";
}

// ============================================
// CHART: Initialize
// ============================================
function initChart() {
  const ctx = document.getElementById("sensor-chart").getContext("2d");
  
  sensorChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        label: "Suhu (°C)",
        data: [],
        borderColor: "#e74c3c",
        backgroundColor: "rgba(231, 76, 60, 0.1)",
        tension: 0.4,
        fill: true,
        pointRadius: 3,
        pointHoverRadius: 5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          mode: "index",
          intersect: false
        }
      },
      scales: {
        x: {
          display: true,
          grid: {
            display: false
          },
          ticks: {
            maxRotation: 0,
            maxTicksLimit: 8
          }
        },
        y: {
          display: true,
          grid: {
            color: "rgba(0,0,0,0.05)"
          }
        }
      },
      interaction: {
        mode: "nearest",
        axis: "x",
        intersect: false
      }
    }
  });
}

// ============================================
// CHART: Update Data
// ============================================
function updateChart(type, data) {
  if (!sensorChart) return;

  const config = {
    temp: {
      label: "Suhu (°C)",
      color: "#e74c3c",
      key: "suhu"
    },
    hum: {
      label: "Kelembapan (%)",
      color: "#3498db",
      key: "kelembapan"
    },
    light: {
      label: "Intensitas Cahaya",
      color: "#f39c12",
      key: "cahaya"
    }
  };

  const cfg = config[type];
  
  sensorChart.data.datasets[0].label = cfg.label;
  sensorChart.data.datasets[0].borderColor = cfg.color;
  sensorChart.data.datasets[0].backgroundColor = cfg.color + "20";
  
  sensorChart.data.labels = data.map(d => d.time);
  sensorChart.data.datasets[0].data = data.map(d => d[cfg.key]);
  
  sensorChart.update();
}

// ============================================
// CHART: Handle Tab Click
// ============================================
function setupChartTabs() {
  document.querySelectorAll(".chart-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".chart-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      
      currentChartType = tab.dataset.chart;
      loadHistoricalData();
    });
  });
}

// ============================================
// ✅ NEW: Load Current Mode
// ============================================
async function loadCurrentMode() {
  try {
    const response = await fetch(`${API_BASE}/api/mode`);
    
    if (!response.ok) {
      console.warn("Failed to fetch mode");
      return;
    }
    
    const data = await response.json();
    currentMode = data.mode;
    
    updateModeUI(currentMode);
    
  } catch (error) {
    console.error("Error loading mode:", error);
  }
}

// ============================================
// ✅ NEW: Update Mode UI
// ============================================
function updateModeUI(mode) {
  const modeBtn = document.getElementById("btn-mode");
  const modeIndicator = document.getElementById("mode-indicator");
  
  if (mode === "AUTO") {
    modeBtn.className = "btn-mode mode-auto";
    modeBtn.innerHTML = "🤖 MODE: AUTO";
    modeIndicator.className = "mode-badge auto";
    modeIndicator.textContent = "AUTO";
  } else {
    modeBtn.className = "btn-mode mode-manual";
    modeBtn.innerHTML = "🎮 MODE: MANUAL";
    modeIndicator.className = "mode-badge manual";
    modeIndicator.textContent = "MANUAL";
  }
}

// ============================================
// ✅ NEW: Toggle Mode
// ============================================
async function toggleMode() {
  const newMode = currentMode === "AUTO" ? "MANUAL" : "AUTO";
  
  const confirmMsg = newMode === "AUTO" 
    ? "Aktifkan mode OTOMATIS? Sistem akan mengontrol atap berdasarkan sensor dan AI."
    : "Aktifkan mode MANUAL? Anda harus mengontrol atap secara manual.";
  
  if (!confirm(confirmMsg)) {
    return;
  }
  
  try {
    showLoading();
    
    const response = await fetch(`${API_BASE}/api/mode/${newMode}`, {
      method: "POST"
    });
    
    if (!response.ok) {
      throw new Error("Failed to change mode");
    }
    
    const data = await response.json();
    
    currentMode = newMode;
    updateModeUI(newMode);
    
    console.log(`Mode changed to: ${newMode}`);
    
    // Refresh notifications
    await loadNotifications();
    
  } catch (error) {
    console.error("Error changing mode:", error);
    alert("Gagal mengubah mode. Coba lagi.");
  } finally {
    hideLoading();
  }
}

// ============================================
// API: Load Sensor Data
// ============================================
async function loadSensorData() {
  try {
    const response = await fetch(`${API_BASE}/api/sensor`);
    
    if (!response.ok) {
      throw new Error("Failed to fetch sensor data");
    }
    
    const data = await response.json();
    
    if (data.error) {
      console.warn("Sensor error:", data.error);
      updateConnectionStatus(false);
      
      document.getElementById("temp-value").textContent = "--";
      document.getElementById("hum-value").textContent = "--";
      document.getElementById("light-value").textContent = "--";
      document.querySelector("#temp-status .status-text").textContent = "-";
      document.querySelector("#hum-status .status-text").textContent = "-";
      document.querySelector("#light-status .status-text").textContent = "-";
      
      return null;
    }
    
    updateConnectionStatus(true);
    
    const temp = parseFloat(data.suhu || 0);
    document.getElementById("temp-value").textContent = temp.toFixed(1);
    document.querySelector("#temp-status .status-text").textContent = getTempStatus(temp);
    
    const hum = parseFloat(data.kelembapan || 0);
    document.getElementById("hum-value").textContent = hum.toFixed(1);
    document.querySelector("#hum-status .status-text").textContent = getHumStatus(hum);
    
    const light = parseInt(data.cahaya || 0);
    document.getElementById("light-value").textContent = light;
    document.querySelector("#light-status .status-text").textContent = getLightStatus(light);
    
    const roofStatus = data.roof || "CLOSED";
    updateRoofStatus(roofStatus);
    
    if (data.hujan === 1) {
      handleRainDetected();
    }
    
    return data;
    
  } catch (error) {
    console.error("Error loading sensor data:", error);
    updateConnectionStatus(false);
    return null;
  }
}

// ============================================
// API: Load AI Prediction
// ============================================
async function loadAIPrediction() {
  try {
    const response = await fetch(`${API_BASE}/api/predict`);
    
    if (!response.ok) {
      throw new Error("Failed to fetch AI prediction");
    }
    
    const data = await response.json();
    
    if (data.error || data.status === "UNKNOWN") {
      console.warn("AI prediction unavailable:", data.reason || data.error);
      document.getElementById("weather-status").textContent = "LOADING...";
      document.getElementById("weather-icon").textContent = "🌡️";
      return;
    }
    
    const weather = data.status.toUpperCase();
    const confidence = data.confidence || 0;
    
    document.getElementById("weather-status").textContent = weather;
    
    const icon = WEATHER_ICONS[weather] || "🌡️";
    document.getElementById("weather-icon").textContent = icon;
    
    console.log(`AI Prediction: ${weather} (${Math.round(confidence * 100)}%)`);
    
    if (weather === "HUJAN" && confidence >= 0.70) {
      const predictionKey = `${weather}-${Math.floor(confidence * 10)}`;
      
      if (lastAIPrediction !== predictionKey) {
        lastAIPrediction = predictionKey;
        handleAIRainPrediction(confidence);
      }
    } else if (weather !== "HUJAN") {
      lastAIPrediction = null;
    }
    
  } catch (error) {
    console.error("Error loading AI prediction:", error);
    document.getElementById("weather-status").textContent = "ERROR";
    document.getElementById("weather-icon").textContent = "⚠️";
  }
}

// ============================================
// API: Load Historical Data
// ============================================
async function loadHistoricalData() {
  try {
    const response = await fetch(`${API_BASE}/api/history/24h`);
    
    if (!response.ok) {
      console.warn("Historical data not available");
      return;
    }
    
    const data = await response.json();
    
    if (data.history && data.history.length > 0) {
      updateChart(currentChartType, data.history);
    }
    
  } catch (error) {
    console.error("Error loading historical data:", error);
  }
}

// ============================================
// API: Load Notifications
// ============================================
async function loadNotifications() {
  try {
    const response = await fetch(`${API_BASE}/api/notifications`);
    
    if (!response.ok) {
      console.warn("Notifications API not available");
      return;
    }
    
    const data = await response.json();
    
    const listEl = document.getElementById("notif-list");
    
    if (!data.notifications || data.notifications.length === 0) {
      listEl.innerHTML = '<div class="notif-empty">Belum ada notifikasi</div>';
      return;
    }
    
    listEl.innerHTML = data.notifications
      .slice(0, 10)
      .map(notif => {
        const type = notif.type || "default";
        return `
          <div class="notif-item ${type}">
            <div class="notif-time">${notif.time}</div>
            <div class="notif-text">${notif.message}</div>
          </div>
        `;
      })
      .join('');
    
  } catch (error) {
    console.error("Error loading notifications:", error);
    document.getElementById("notif-list").innerHTML = 
      '<div class="notif-empty">Belum ada notifikasi</div>';
  }
}

// ============================================
// UI: Update Roof Status
// ============================================
function updateRoofStatus(status) {
  const roofEl = document.getElementById("roof-status");
  const btnEl = document.getElementById("btn-control");
  
  status = status.toUpperCase();
  
  if (status === "OPEN") {
    roofEl.className = "roof-indicator roof-open";
    roofEl.textContent = "▲ ATAP TERBUKA";
    btnEl.className = "btn-close";
    btnEl.textContent = "TUTUP ATAP";
  } else {
    roofEl.className = "roof-indicator roof-closed";
    roofEl.textContent = "▼ ATAP TERTUTUP";
    btnEl.className = "btn-open";
    btnEl.textContent = "BUKA ATAP";
  }
  
  // ✅ Disable control button if AUTO mode
  if (currentMode === "AUTO") {
    btnEl.disabled = true;
    btnEl.style.opacity = "0.5";
    btnEl.style.cursor = "not-allowed";
  } else {
    btnEl.disabled = false;
    btnEl.style.opacity = "1";
    btnEl.style.cursor = "pointer";
  }
}

// ============================================
// NOTIFICATION: Rain Detected
// ============================================
function handleRainDetected() {
  const now = Date.now();
  
  if (now - lastRainWarning < 60000) {
    return;
  }
  
  lastRainWarning = now;
  
  console.log("🌧️ RAIN DETECTED!");
  
  showPushNotification("🌧️ HUJAN TERDETEKSI!", {
    body: "Sensor mendeteksi hujan. Atap akan ditutup otomatis.",
    tag: "rain-detected",
    requireInteraction: true
  });
  
  setTimeout(() => loadNotifications(), 1000);
}

// ============================================
// NOTIFICATION: AI Rain Prediction
// ============================================
function handleAIRainPrediction(confidence) {
  const now = Date.now();
  
  if (now - lastAIWarning < 180000) {
    return;
  }
  
  lastAIWarning = now;
  
  const confidencePercent = Math.round(confidence * 100);
  
  console.log(`⚠️ AI PREDICTION: Rain coming (${confidencePercent}%)`);
  
  showPushNotification("⚠️ PREDIKSI AI: HUJAN DATANG", {
    body: `Kemungkinan hujan dalam 5 menit: ${confidencePercent}%. Bersiap untuk menutup atap.`,
    tag: "ai-rain-warning",
    requireInteraction: false
  });
  
  setTimeout(() => loadNotifications(), 1000);
}

// ============================================
// API: Send Control Command
// ============================================
async function sendControlCommand(action) {
  // ✅ Check if manual mode
  if (currentMode === "AUTO") {
    alert("Mode sedang AUTO. Ubah ke MANUAL untuk kontrol manual.");
    return;
  }
  
  try {
    showLoading();
    
    const response = await fetch(`${API_BASE}/api/control/${action}`, {
      method: "POST"
    });
    
    if (!response.ok) {
      throw new Error("Failed to send control command");
    }
    
    const data = await response.json();
    
    console.log("Control response:", data);
    
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    await loadAllData();
    
  } catch (error) {
    console.error("Error sending control command:", error);
    alert("Gagal mengirim perintah. Coba lagi.");
  } finally {
    hideLoading();
  }
}

// ============================================
// UI: Handle Button Click
// ============================================
function handleControlClick() {
  if (currentMode === "AUTO") {
    alert("Mode sedang AUTO. Ubah ke MANUAL untuk kontrol manual.");
    return;
  }
  
  const roofEl = document.getElementById("roof-status");
  const isOpen = roofEl.classList.contains("roof-open");
  
  const action = isOpen ? "TUTUP" : "BUKA";
  
  if (confirm(`Yakin ingin ${action} atap?`)) {
    sendControlCommand(action);
  }
}

// ============================================
// MAIN: Load All Data
// ============================================
async function loadAllData() {
  await loadSensorData();
  await loadNotifications();
  await loadHistoricalData();
  await loadCurrentMode(); // ✅ Load mode status
}

// ============================================
// MAIN: Check AI Prediction
// ============================================
async function checkAIPrediction() {
  if (!isLoading) {
    await loadAIPrediction();
  }
}

// ============================================
// MAIN: Start Polling
// ============================================
function startPolling() {
  if (pollTimer) clearInterval(pollTimer);
  if (aiCheckTimer) clearInterval(aiCheckTimer);
  
  pollTimer = setInterval(() => {
    if (!isLoading) {
      loadAllData();
    }
  }, POLL_INTERVAL);
  
  aiCheckTimer = setInterval(() => {
    checkAIPrediction();
  }, AI_CHECK_INTERVAL);
  
  console.log("✅ Polling started:");
  console.log(`  - Sensor data: every ${POLL_INTERVAL / 1000}s`);
  console.log(`  - AI prediction: every ${AI_CHECK_INTERVAL / 1000}s`);
}

// ============================================
// MAIN: Initialize App
// ============================================
async function initApp() {
  console.log("🏠 Smart Roof Web App initialized");
  
  const notifGranted = await requestNotificationPermission();
  if (notifGranted) {
    console.log("✅ Notification permission granted");
  } else {
    console.warn("⚠️ Notification permission denied");
  }
  
  setInterval(updateClock, 1000);
  updateClock();
  
  initChart();
  setupChartTabs();
  
  // ✅ Attach button handlers
  document.getElementById("btn-control").addEventListener("click", handleControlClick);
  document.getElementById("btn-mode").addEventListener("click", toggleMode);
  
  console.log("📡 Loading initial data...");
  await loadAllData();
  await loadAIPrediction();
  
  startPolling();
  
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      if (pollTimer) clearInterval(pollTimer);
      if (aiCheckTimer) clearInterval(aiCheckTimer);
      console.log("⏸️ App hidden - polling stopped");
    } else {
      console.log("▶️ App visible - resuming...");
      loadAllData();
      loadAIPrediction();
      startPolling();
    }
  });
  
  console.log("✅ App ready!");
}

// ============================================
// ENTRY POINT
// ============================================
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp);
} else {
  initApp();
}