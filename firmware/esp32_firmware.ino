/**
 * ESP32 VESC Telemetry Firmware
 * ─────────────────────────────
 * Reads telemetry from a VESC motor controller over UART2 (Serial2),
 * then POSTs a JSON payload to a cloud backend every SEND_INTERVAL_MS.
 *
 * Hardware wiring:
 *   VESC 5V  → ESP32 VIN (or 5V pin)
 *   VESC GND → ESP32 GND
 *   VESC TX  → ESP32 GPIO16 (Serial2 RX)
 *   VESC RX  → ESP32 GPIO17 (Serial2 TX)
 *
 * VESC Tool settings required:
 *   App to use : UART
 *   UART baud  : 115200
 *
 * Libraries needed (install via Arduino Library Manager or .zip):
 *   - VescUart  (by SolidGeek): https://github.com/SolidGeek/VescUart
 *   - WiFiClientSecure (bundled with ESP32 Arduino core)
 *   - ArduinoJson (by bblanchon) >= 6.x
 *
 * ─── CONFIGURE THESE VALUES BEFORE FLASHING ──────────────────────────────
 */

// Wi-Fi credentials
const char* WIFI_SSID     = "YOUR_WIFI_SSID";       // <-- change me
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";    // <-- change me

// Backend endpoint (your Vercel deployment URL, no trailing slash)
const char* API_BASE_URL  = "https://your-app.vercel.app"; // <-- change me

// Shared API key — must match API_KEY env var set in Vercel
const char* API_KEY       = "YOUR_API_KEY_HERE";     // <-- change me

// How often to send telemetry (milliseconds)
const unsigned long SEND_INTERVAL_MS = 200;

// Serial2 pins
const int RX2_PIN = 16;
const int TX2_PIN = 17;

// ─────────────────────────────────────────────────────────────────────────────

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "VescUart.h"

VescUart vesc;
unsigned long lastSendTime = 0;

// ─── SETUP ───────────────────────────────────────────────────────────────────

void setup() {
  Serial.begin(115200);
  Serial.println("\n[BOOT] ESP32 VESC Telemetry starting...");

  // VESC UART on Serial2
  Serial2.begin(115200, SERIAL_8N1, RX2_PIN, TX2_PIN);
  vesc.setSerialPort(&Serial2);

  // Connect to Wi-Fi
  Serial.printf("[WiFi] Connecting to %s", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.printf("\n[WiFi] Connected. IP: %s\n", WiFi.localIP().toString().c_str());
}

// ─── LOOP ────────────────────────────────────────────────────────────────────

void loop() {
  unsigned long now = millis();
  if (now - lastSendTime < SEND_INTERVAL_MS) return;
  lastSendTime = now;

  // Request telemetry values from VESC (blocking, ~10 ms)
  if (!vesc.getVescValues()) {
    Serial.println("[VESC] Failed to read values — check wiring and baud rate");
    return;
  }

  // Build JSON payload
  // Fields mirror the struct members of VescUart::data (VescValues)
  StaticJsonDocument<256> doc;
  doc["timestamp"]      = now;                           // ms since boot
  doc["voltage"]        = vesc.data.inpVoltage;         // V
  doc["motor_current"]  = vesc.data.avgMotorCurrent;    // A
  doc["battery_current"]= vesc.data.avgInputCurrent;    // A
  doc["rpm"]            = vesc.data.rpm;                // electrical RPM
  doc["duty"]           = vesc.data.dutyCycleNow;       // 0.0 – 1.0
  doc["mosfet_temp"]    = vesc.data.tempMosfet;         // °C

  String payload;
  serializeJson(doc, payload);

  Serial.printf("[TX] %s\n", payload.c_str());

  // Send HTTPS POST
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WiFi] Lost connection — skipping send");
    return;
  }

  WiFiClientSecure client;
  // For development/demo: skip certificate verification.
  // In production, set the root CA with client.setCACert(rootCACert);
  client.setInsecure();

  HTTPClient http;
  String url = String(API_BASE_URL) + "/api/telemetry";
  http.begin(client, url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("x-api-key", API_KEY);  // authentication header

  int httpCode = http.POST(payload);
  if (httpCode > 0) {
    Serial.printf("[HTTP] Response: %d\n", httpCode);
  } else {
    Serial.printf("[HTTP] Error: %s\n", http.errorToString(httpCode).c_str());
  }
  http.end();
}
