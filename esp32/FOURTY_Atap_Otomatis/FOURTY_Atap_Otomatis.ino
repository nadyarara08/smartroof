#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <ESP32Servo.h>

// ================= PIN =================
#define DHTPIN 4
#define DHTTYPE DHT11
#define RAIN_PIN 34
#define LDR_PIN 35

#define SERVO1_PIN 18
#define SERVO2_PIN 19
#define BUZZER_PIN 13

// ================= SERVO ANGLE =================
#define SERVO_OPEN  0
#define SERVO_CLOSE 180

// ================= WIFI =================
const char* ssid = "Arkan";
const char* password = "Persissolo";

// ================= MQTT =================
const char* mqtt_server = "broker.hivemq.com";
const char* topic_pub  = "sensor/smartroof/data";
const char* topic_cmd  = "control/smartroof/cmd";
const char* topic_mode = "control/smartroof/mode";

// ================= OBJECT =================
WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

Servo servo1;
Servo servo2;

// ================= STATE =================
bool autoMode = true;
bool hujanSebelumnya = false;
String currentStatus = "BUKA";  // ✅ Track status atap

// ================= BUZZER =================
unsigned long lastBeep = 0;
int beepCount = 0;
int beepTarget = 0;
bool buzzerState = false;
bool isBeeping = false;

// ================= SERVO CONTROL =================
void bukaAtap() {
  Serial.println("🔓 MEMBUKA ATAP...");
  servo1.write(SERVO_OPEN);
  servo2.write(SERVO_OPEN);
  currentStatus = "BUKA";
  delay(500);  // ✅ Tunggu servo selesai
  Serial.println("✅ Atap TERBUKA");
}

void tutupAtap() {
  Serial.println("🔒 MENUTUP ATAP...");
  servo1.write(SERVO_CLOSE);
  servo2.write(SERVO_CLOSE);
  currentStatus = "TUTUP";
  delay(500);  // ✅ Tunggu servo selesai
  Serial.println("✅ Atap TERTUTUP");
}

// ================= BUZZER =================
void startBeep(int count) {
  beepTarget = count * 2;
  beepCount = 0;
  isBeeping = true;
  lastBeep = millis();
}

void handleBeep() {
  if (!isBeeping) return;

  if (beepCount >= beepTarget) {
    digitalWrite(BUZZER_PIN, LOW);
    isBeeping = false;
    return;
  }

  if (millis() - lastBeep >= 300) {
    lastBeep = millis();
    buzzerState = !buzzerState;
    digitalWrite(BUZZER_PIN, buzzerState);
    beepCount++;
  }
}

// ================= WIFI =================
void setup_wifi() {
  Serial.print("📡 Connecting to WiFi");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n✅ WiFi connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

// ================= MQTT CALLBACK =================
void callback(char* topic, byte* payload, unsigned int length) {
  // ✅ Debug: Print raw message
  Serial.print("📥 Message from [");
  Serial.print(topic);
  Serial.print("]: ");
  
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);
  
  // ✅ Parse JSON
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, payload, length);
  
  if (error) {
    Serial.print("❌ JSON parse error: ");
    Serial.println(error.c_str());
    return;
  }

  // ===== HANDLE MODE =====
  if (String(topic) == topic_mode) {
    const char* mode = doc["mode"];
    if (mode) {
      autoMode = (strcmp(mode, "AUTO") == 0);
      Serial.print("🤖 Mode changed to: ");
      Serial.println(autoMode ? "AUTO" : "MANUAL");
    }
    return;
  }

  // ===== HANDLE COMMAND (MANUAL MODE ONLY) =====
  if (String(topic) == topic_cmd) {
    if (autoMode) {
      Serial.println("⚠️ Command ignored - Auto mode active");
      return;
    }
    
    const char* aksi = doc["aksi"];
    int buzzer = doc["buzzer"] | 0;

    if (aksi) {
      Serial.print("🎮 Executing command: ");
      Serial.println(aksi);
      
      if (strcmp(aksi, "BUKA") == 0) {
        bukaAtap();
      } 
      else if (strcmp(aksi, "TUTUP") == 0) {
        tutupAtap();
      }
    }

    if (buzzer > 0 && !isBeeping) {
      startBeep(buzzer);
    }
  }
}

// ================= MQTT CONNECT =================
void reconnect() {
  while (!client.connected()) {
    Serial.print("📡 Connecting to MQTT...");
    
    String clientId = "ESP32_SMARTROOF_" + String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println(" ✅ Connected!");
      
      // ✅ Subscribe to topics
      client.subscribe(topic_cmd);
      client.subscribe(topic_mode);
      
      Serial.println("✅ Subscribed to control topics");
    } else {
      Serial.print(" ❌ Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 2s...");
      delay(2000);
    }
  }
}

// ================= SETUP =================
void setup() {
  Serial.begin(115200);
  Serial.println("\n🚀 SMART ROOF ESP32 STARTING...");

  // ✅ Setup pins
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  // ✅ Setup sensors
  dht.begin();

  // ✅ Setup servos
  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);
  bukaAtap();  // Default: Atap terbuka

  // ✅ Connect WiFi
  setup_wifi();

  // ✅ Connect MQTT
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  
  Serial.println("✅ Setup complete!");
}

// ================= LOOP =================
void loop() {
  // ✅ Maintain MQTT connection
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  handleBeep();

  // ===== READ SENSORS =====
  float suhu = dht.readTemperature();
  float kelembapan = dht.readHumidity();
  int cahaya = analogRead(LDR_PIN);
  bool hujanSekarang = (analogRead(RAIN_PIN) < 2000);

  // ===== AUTO MODE LOGIC =====
  if (autoMode) {
    // Hujan terdeteksi pertama kali -> Tutup atap
    if (hujanSekarang && !hujanSebelumnya) {
      Serial.println("🌧️ HUJAN TERDETEKSI!");
      tutupAtap();
      startBeep(3);
      hujanSebelumnya = true;
    }

    // Hujan berhenti -> Buka atap
    if (!hujanSekarang && hujanSebelumnya) {
      Serial.println("☀️ HUJAN BERHENTI!");
      bukaAtap();
      hujanSebelumnya = false;
    }
  }

  // ===== PUBLISH DATA TO MQTT =====
  StaticJsonDocument<256> doc;
  doc["suhu"] = isnan(suhu) ? 0 : suhu;
  doc["kelembapan"] = isnan(kelembapan) ? 0 : kelembapan;
  doc["cahaya"] = cahaya;
  doc["hujan"] = hujanSekarang ? 1 : 0;
  doc["mode"] = autoMode ? "AUTO" : "MANUAL";
  doc["atap"] = currentStatus;  // ✅ Status atap (BUKA/TUTUP)

  char buffer[256];
  serializeJson(doc, buffer);
  
  if (client.publish(topic_pub, buffer)) {
    Serial.print("📤 Published: ");
    Serial.println(buffer);
  } else {
    Serial.println("❌ Publish failed!");
  }

  delay(5000);  // Kirim data tiap 5 detik
}