const API_CONTROL = "http://localhost:5000/control";
const API_STATUS  = "http://localhost:5000/status";

const weatherEl = document.getElementById("weather");
const roofEl = document.getElementById("roof-status");
const btn = document.getElementById("btn-control");

let roofOpen = true;

// ==========================
// FETCH STATUS
// ==========================
async function fetchStatus() {
  const res = await fetch(API_STATUS);
  const data = await res.json();

  weatherEl.innerText = data.cuaca.toUpperCase();
  document.getElementById("temp").innerText = data.suhu + " °C";
  document.getElementById("hum").innerText = data.kelembapan + " %";
  document.getElementById("light").innerText = data.cahaya;

  roofOpen = data.atap === "BUKA";

  roofEl.innerText = roofOpen ? "▲ ATAP TERBUKA" : "▼ ATAP TERTUTUP";
  btn.innerText = roofOpen ? "TUTUP ATAP" : "BUKA ATAP";
}

// ==========================
// CONTROL
// ==========================
btn.onclick = async () => {
  const aksi = roofOpen ? "TUTUP" : "BUKA";
  await fetch(API_CONTROL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ aksi })
  });
};

// refresh tiap 2 detik
setInterval(fetchStatus, 2000);
fetchStatus();
