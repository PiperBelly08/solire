#include <WiFiManager.h>
#include <MQTT.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>

// WiFi credentials will be managed by WiFiManager
// MQTT Broker details
const char* mqtt_server = "piperbelly008.cloud.shiftr.io";
const int mqtt_port = 1883; // Default MQTT port
const char* mqtt_user = "piperbelly008";
const char* mqtt_password = "XMursJDSPQStqLz6";

// MQTT Topic for combined sensor data
const char* topic = "Sensors"; // Keep existing subscribe topic

WiFiClient net;
MQTTClient client;

unsigned long lastMillis = 0;

const char* AP_NAME = "SolireSense";
const char* MQTT_ID = "SolireSense";

// PH
#define DMS_PIN 13
#define ADC_PIN 34

// Moisture
#define MOISTURE_SENSOR_ANALOG_PIN 33
#define MOISTURE_SENSOR_DIGITAL_PIN 32

// Temperature
#define ONE_WIRE_BUS 4

// Buzzer
#define BUZZER_PIN 16

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void connectMqtt() {
  Serial.print("\nConnecting To MQTT Server!\n");
  while (!client.connect(MQTT_ID, mqtt_user, mqtt_password)) {
    Serial.print(".");
    delay(1000);
  }

  Serial.println("\nConnected!");

  client.subscribe(topic);
}

void messageReceived(String &topic, String &payload) {
  Serial.println(topic + ": " + payload);
}

void setupWiFi() {
  WiFiManager wm;
  // Reset settings - for testing
  // wm.resetSettings();

  if (!wm.autoConnect(AP_NAME)) {
    Serial.println("Failed to connect or timed out");
    delay(3000);
    ESP.restart();
  }

  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

int deviceCount = 0;
int phAdc;
float lastReading;
float pH;
float tempC;
float tempF;
int moistureLevelAnalog;
int moistureLevelDigital;
void setup() {
  Serial.begin(115200);
  Serial.println("Starting...");

  sensors.begin();

  // Locate the devices on the bus:
  Serial.println("Locating devices...");
  Serial.print("Found ");
  Serial.print(sensors.getDeviceCount());
  Serial.println(" devices");

  // Moisture
  pinMode(MOISTURE_SENSOR_ANALOG_PIN, INPUT);
  pinMode(MOISTURE_SENSOR_DIGITAL_PIN, INPUT_PULLUP);

  analogReadResolution(10);

  // PH
  pinMode(DMS_PIN, OUTPUT);
  digitalWrite(DMS_PIN, HIGH); // Turn off DMS

  // Buzzer
  pinMode(BUZZER_PIN, OUTPUT);

  setupWiFi();

  client.begin("piperbelly008.cloud.shiftr.io", net);
  client.onMessage(messageReceived);
  connectMqtt();
}

void loop() {
  client.loop();

  // Check if connected
  if (!client.connected()) {
    connectMqtt();
  }

  // --- Read Sensors ---

  // Temperature
  sensors.requestTemperatures();
  tempC = sensors.getTempCByIndex(0);
  tempF = sensors.getTempFByIndex(0);

  // Moisture
  moistureLevelAnalog = analogRead(MOISTURE_SENSOR_ANALOG_PIN);
  moistureLevelDigital = digitalRead(MOISTURE_SENSOR_DIGITAL_PIN);
  int moisturePercent = map(moistureLevelAnalog, 300, 1023, 100, 0);
  moisturePercent = constrain(moisturePercent, 0, 100);

  // PH
  digitalWrite(DMS_PIN, LOW); // Turn on DMS
  delay(1000 * 10);
  phAdc = analogRead(ADC_PIN);
  pH = (-0.023 * phAdc) + 12.627;
  lastReading = pH;
  digitalWrite(DMS_PIN, HIGH);
  delay(1000 * 3);

  // --- Publish all data to a single topic ---

  DynamicJsonDocument allSensorDoc(256); // Increased size to accommodate all data

  // Add Temperature data
  allSensorDoc["temperature_c"] = tempC;
  allSensorDoc["temperature_f"] = tempF;

  // Add Moisture data
  allSensorDoc["moisture_analog"] = moistureLevelAnalog;
  allSensorDoc["moisture_digital"] = moistureLevelDigital;
  allSensorDoc["moisture_percent"] = moisturePercent;

  // Add PH data
  allSensorDoc["ph_adc"] = phAdc;
  allSensorDoc["ph_value"] = lastReading;

  char combinedJsonBuffer[256]; // Increased buffer size
  serializeJson(allSensorDoc, combinedJsonBuffer);
  client.publish(topic, combinedJsonBuffer);
  Serial.print("Published to ");
  Serial.print(topic);
  Serial.print(": ");
  Serial.println(combinedJsonBuffer);

  Serial.println(); // Add a newline for readability in the serial monitor
  
  tone(BUZZER_PIN, 1000); delay(150); noTone(BUZZER_PIN); delay(50);
}
