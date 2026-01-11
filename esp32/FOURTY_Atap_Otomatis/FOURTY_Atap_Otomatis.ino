#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <ESP32Servo.h>

// ===== PIN =====
#define DHTPIN 4
#define DHTTYPE DHT11
#define RAIN_PIN 34
#define LDR_PIN 35
#define SERVO_PIN 18
#define BUZZER_PIN 13

// ===== WIFI =====
const char* ssid = "MODAL DONG";
const char* password = "AbrisamAzka";

// ===== MQTT =====
const char* mqtt_server = "broker.hivemq.com";
const char* topic_pub  = "sensor/smartroof/data";
const char* topic_cmd  = "control/smartroof/cmd";
const char* topic_mode = "control/smartroof/mode";

// ===== OBJECT =====
WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);
Servo servo;

// ===== SYSTEM STATE =====
bool autoMode = true;   // default AUTO

// ===== BUZZER STATE =====
unsigned long lastBeep = 0;
int beepCount = 0;
int beepTarget = 0;
bool buzzerState = false;
bool isBeeping = false;

// ===== BUZZER FUNCTION =====
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

// ===== WIFI CONNECT =====
void setup_wifi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  Serial.print("Connecting WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.println(WiFi.localIP());
}

// ===== MQTT CALLBACK =====
void callback(char* topic, byte* payload, unsigned int length) {
  StaticJsonDocument<200> doc;
  deserializeJson(doc, payload, length);

  // ===== MODE =====
  if (String(topic) == topic_mode) {
    const char* mode = doc["mode"];
    if (mode) {
      autoMode = (strcmp(mode, "AUTO") == 0);
    }
    return;
  }

  // ===== COMMAND =====
  if (String(topic) == topic_cmd && !autoMode) {
    const char* aksi = doc["aksi"];
    int buzzer = doc["buzzer"] | 0;

    if (aksi) {
      if (strcmp(aksi, "TUTUP") == 0) servo.write(90);
      if (strcmp(aksi, "BUKA")  == 0) servo.write(0);
    }

    if (buzzer > 0 && !isBeeping) {
      startBeep(buzzer);
    }
  }
}

// ===== MQTT RECONNECT =====
void reconnect() {
  while (!client.connected()) {
    if (client.connect("ESP32_SMARTROOF_AUTO")) {
      client.subscribe(topic_cmd);
      client.subscribe(topic_mode);
    } else {
      delay(2000);
    }
  }
}

// ===== SETUP =====
void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  dht.begin();
  servo.attach(SERVO_PIN);
  servo.write(0);

  setup_wifi();

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

// ===== LOOP =====
void loop() {
  if (!client.connected()) reconnect();
  client.loop();
  handleBeep();

  float suhu = dht.readTemperature();
  float kelembapan = dht.readHumidity();
  int cahaya = analogRead(LDR_PIN);
  int hujan = analogRead(RAIN_PIN) < 2000 ? 1 : 0;

  // ===== PRIORITAS HUJAN =====
  if (hujan == 1) {
    servo.write(90);            // TUTUP
    if (!isBeeping) startBeep(3);
  }

  // ===== KIRIM DATA =====
  StaticJsonDocument<200> doc;
  doc["suhu"] = suhu;
  doc["kelembapan"] = kelembapan;
  doc["cahaya"] = cahaya;
  doc["hujan"] = hujan;
  doc["mode"] = autoMode ? "AUTO" : "MANUAL";

  char buffer[256];
  serializeJson(doc, buffer);
  client.publish(topic_pub, buffer);

  delay(5000);
}
