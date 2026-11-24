
#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <math.h>

const char* DEVICE_ID = "esp32-wokwi-01";
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";

// Wokwi VS Code gateway address
const char* API_URL = "http://host.wokwi.internal:8000/telemetry";

const unsigned long SEND_INTERVAL_MS = 1000;
unsigned long lastSend = 0;
unsigned long sampleNumber = 0;

struct SensorData {
  float vibrationX;
  float vibrationY;
  float vibrationZ;
  float temperatureC;
  float currentA;
};

SensorData readSimulatedSensors() {
  SensorData data;
  int phase = (sampleNumber / 20) % 4;
  float t = sampleNumber * 0.12f;
  float noise = (float)(esp_random() % 1000) / 1000.0f - 0.5f;

  if (phase == 0) {
    data.vibrationX = 0.18f + 0.02f * sinf(t) + noise * 0.02f;
    data.vibrationY = 0.17f + 0.02f * cosf(t) + noise * 0.02f;
    data.vibrationZ = 0.19f + noise * 0.02f;
    data.temperatureC = 30.0f + noise;
    data.currentA = 0.45f + noise * 0.04f;
  } else if (phase == 1) {
    data.vibrationX = 1.15f + noise * 0.12f;
    data.vibrationY = 0.25f + noise * 0.04f;
    data.vibrationZ = 0.25f + noise * 0.04f;
    data.temperatureC = 31.0f + noise;
    data.currentA = 0.50f + noise * 0.04f;
  } else if (phase == 2) {
    data.vibrationX = 0.20f + noise * 0.02f;
    data.vibrationY = 0.20f + noise * 0.02f;
    data.vibrationZ = 0.20f + noise * 0.02f;
    data.temperatureC = 72.0f + noise * 2.0f;
    data.currentA = 0.48f + noise * 0.04f;
  } else {
    data.vibrationX = 0.22f + noise * 0.02f;
    data.vibrationY = 0.22f + noise * 0.02f;
    data.vibrationZ = 0.22f + noise * 0.02f;
    data.temperatureC = 32.0f + noise;
    data.currentA = 2.20f + noise * 0.12f;
  }

  return data;
}

void connectWiFi() {
  Serial.print("Connecting to Wokwi WiFi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void sendTelemetry(const SensorData& s) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Reconnecting...");
    connectWiFi();
  }

  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");

  JsonDocument doc;
  doc["device_id"] = DEVICE_ID;
  doc["vibration_x"] = s.vibrationX;
  doc["vibration_y"] = s.vibrationY;
  doc["vibration_z"] = s.vibrationZ;
  doc["temperature_c"] = s.temperatureC;
  doc["current_a"] = s.currentA;

  String payload;
  serializeJson(doc, payload);

  Serial.println("Sending: " + payload);

  int responseCode = http.POST(payload);

  if (responseCode > 0) {
    Serial.printf("Backend HTTP status: %d\n", responseCode);
    Serial.println("Backend response: " + http.getString());
  } else {
    Serial.printf("HTTP request failed: %s\n",
                  http.errorToString(responseCode).c_str());
  }

  http.end();
}

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("ESP32 telemetry simulator started");
  connectWiFi();
}

void loop() {
  if (millis() - lastSend >= SEND_INTERVAL_MS) {
    lastSend = millis();

    SensorData s = readSimulatedSensors();

    Serial.printf(
      "Vibration: %.3f, %.3f, %.3f | Temperature: %.2f C | Current: %.3f A\n",
      s.vibrationX, s.vibrationY, s.vibrationZ,
      s.temperatureC, s.currentA
    );

    sendTelemetry(s);
    sampleNumber++;
  }
}
