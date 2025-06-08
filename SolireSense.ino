#include <WiFiManager.h>
#include <MQTT.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// WiFi credentials will be managed by WiFiManager
// MQTT Broker details
const char* mqtt_server = "piperbelly008.cloud.shiftr.io";
const int mqtt_port = 1883; // Default MQTT port
const char* mqtt_user = "piperbelly008";
const char* mqtt_password = "XMursJDSPQStqLz6";

// MQTT Topic to publish to
const char* publish_topic = "Sensors";
// MQTT Topic to subscribe to
const char* subscribe_topic = "Sensors";

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

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void connectMqtt() {
  Serial.print("\nConnecting To MQTT Server!\n");
  while (!client.connect(MQTT_ID, mqtt_user, mqtt_password)) {
    Serial.print(".");
    delay(1000);
  }

  Serial.println("\nConnected!");

  client.subscribe(subscribe_topic);
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

  setupWiFi();

  client.begin("piperbelly008.cloud.shiftr.io", net);
  client.onMessage(messageReceived);
  connectMqtt();
}

void loop() {
  client.loop();

  // check if connected
  if (!client.connected()) {
    connectMqtt();
  }

  // Temperature
  // Send the command for all devices on the bus to perform a temperature conversion:
  sensors.requestTemperatures();

  for (int i = 0;  i < deviceCount;  i++) {
    Serial.print("Sensor ");
    Serial.print(i + 1);
    Serial.print(" : ");
    tempC = sensors.getTempCByIndex(i);
    tempF = sensors.getTempFByIndex(i);
    Serial.print(tempC);
    Serial.print(" \xC2\xB0"); // shows degree symbol
    Serial.print("C  |  ");
    Serial.print(tempF);
    Serial.print(" \xC2\xB0"); // shows degree symbol
    Serial.println("F");
  }

  Serial.println();

  // Moisture
  Serial.println();

  Serial.print("Mo: ");
  moistureLevelAnalog = analogRead(MOISTURE_SENSOR_ANALOG_PIN);
  Serial.print(moistureLevelAnalog);
  Serial.print("(A) | ");
  moistureLevelDigital = digitalRead(MOISTURE_SENSOR_DIGITAL_PIN);
  Serial.print(moistureLevelDigital);
  Serial.print("(D)");
  Serial.println();
  int moisturePercent = map(moistureLevelAnalog, 300, 1023, 100, 0);
  moisturePercent = constrain(moisturePercent, 0, 100);
  Serial.print("Moisture: ");
  Serial.print(moisturePercent);
  Serial.println("%");
  Serial.println();

  Serial.println();

  // PH
  digitalWrite(DMS_PIN, LOW); // Turn on DMS
  delay(1000 * 10);

  phAdc = analogRead(ADC_PIN);
  pH = (-0.023 * phAdc) + 12.627;
  if (pH != lastReading) { 
    lastReading = pH; 
  }
  Serial.print("PH ADC: ");
  Serial.print(phAdc);
  Serial.print(" | pH: ");
  Serial.println(lastReading, 1);

  digitalWrite(DMS_PIN, HIGH);
  delay(1000 * 3);

  Serial.println();

  // Construct JSON string
  String payload = "{";
  payload += "\"temperature_c\":" + String(tempC, 2) + ",";
  payload += "\"temperature_f\":" + String(tempF, 2) + ",";
  payload += "\"moisture_percent\":" + String(moisturePercent) + ",";
  // payload += "\"ph_adc\":" + String(phAdc) + ",";
  payload += "\"ph_value\":" + String(lastReading, 2);
  payload += "}";

  // Debug: print the payload
  Serial.println("Publishing payload:");
  Serial.println(payload);

  // Publish to MQTT
  client.publish(publish_topic, payload);
}
