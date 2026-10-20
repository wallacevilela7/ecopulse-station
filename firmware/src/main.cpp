#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <DHT.h>
#include <ArduinoJson.h>

#include "config.h.example" // Substitua por "config.h" em producao

// Instâncias dos Sensores
#define DHTTYPE DHT22
DHT dht(PIN_DHT22, DHTTYPE);
Adafruit_BMP280 bmp; // I2C

unsigned long lastTelemetryTime = 0;
bool bmpAvailable = false;

// Prototipação
void connectWiFi();
void readAndTransmitTelemetry();
void checkLocalSafetyLogic(float rainPct, float pressure, float mqVoltage);

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n==============================================");
  Serial.println("  EcoPulse Station - Firmware ESP32 Inicializado");
  Serial.println("  UNIP PIM II / PD-II - Smart Cities");
  Serial.println("==============================================");

  pinMode(PIN_ALARM_LED, OUTPUT);
  pinMode(PIN_WIFI_LED, OUTPUT);
  digitalWrite(PIN_ALARM_LED, LOW);
  digitalWrite(PIN_WIFI_LED, LOW);

  // Configuração da resolução do ADC para 12 bits (0 a 4095)
  analogReadResolution(12);

  // Inicializa barramento I2C e sensor BMP280
  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
  if (bmp.begin(0x76)) {
    Serial.println("[BMP280] Sensor de Pressao/Altimetria detectado no endereco 0x76.");
    bmpAvailable = true;
  } else if (bmp.begin(0x77)) {
    Serial.println("[BMP280] Sensor de Pressao/Altimetria detectado no endereco 0x77.");
    bmpAvailable = true;
  } else {
    Serial.println("[BMP280] ALERTA: Sensor nao encontrado no barramento I2C!");
    bmpAvailable = false;
  }

  // Inicializa DHT22
  dht.begin();
  Serial.println("[DHT22] Sensor de Temperatura e Umidade inicializado.");

  // Conecta ao Wi-Fi
  connectWiFi();
}

void loop() {
  // Verifica conexão Wi-Fi
  if (WiFi.status() != WL_CONNECTED) {
    digitalWrite(PIN_WIFI_LED, LOW);
    connectWiFi();
  } else {
    digitalWrite(PIN_WIFI_LED, HIGH);
  }

  // Ciclo não-bloqueante de telemetria
  unsigned long currentMillis = millis();
  if (currentMillis - lastTelemetryTime >= TELEMETRY_INTERVAL_MS) {
    lastTelemetryTime = currentMillis;
    readAndTransmitTelemetry();
  }

  delay(50);
}

void connectWiFi() {
  Serial.printf("[Wi-Fi] Conectando ao ponto de acesso: %s ...\n", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long startAttempt = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startAttempt < 15000) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[Wi-Fi] Conectado com sucesso!");
    Serial.printf("[Wi-Fi] IP Local: %s | RSSI: %d dBm\n", WiFi.localIP().toString().c_str(), WiFi.RSSI());
  } else {
    Serial.println("\n[Wi-Fi] Falha ao conectar. Retentando no proximo ciclo.");
  }
}

void readAndTransmitTelemetry() {
  Serial.println("\n--- [Ciclo de Coleta de Sensores] ---");

  // 1. Leitura DHT22 (Digital One-Wire)
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  String dhtStatus = "OK";
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("[DHT22] Erro na leitura de dados (NaN).");
    temperature = 25.0; // fallback de seguranca
    humidity = 60.0;
    dhtStatus = "READ_ERROR";
  }

  // 2. Leitura BMP280 (Digital I2C)
  float pressure = 1013.25;
  float altitude = 760.0;
  float bmpTemp = temperature;
  String bmpStatus = "I2C_ERROR";
  if (bmpAvailable) {
    pressure = bmp.readPressure() / 100.0F; // Pa para hPa
    altitude = bmp.readAltitude(1013.25);
    bmpTemp = bmp.readTemperature();
    bmpStatus = "OK";
  }

  // 3. Leitura LDR (GPIO 34 - ADC1)
  int ldrRaw = analogRead(PIN_LDR);
  float luminosityPct = (ldrRaw / 4095.0F) * 100.0F;

  // 4. Leitura MQ-135 (GPIO 32 - ADC1 com Divisor 1k/2k)
  int mqRaw = analogRead(PIN_MQ135);
  // Reconstituição da tensão original de 5V antes do divisor (fator 1.5x)
  float mqVoltage = (mqRaw / 4095.0F) * 3.3F * 1.5F;
  float airQualityPpm = mqVoltage * 120.0F; // Estimativa de PPM
  bool isWarmedUp = (millis() >= 180000); // 3 minutos

  // 5. Leitura Sensor de Chuva (GPIO 35 - ADC1)
  int rainRaw = analogRead(PIN_RAIN);
  // Resistência complementar invertida (seco = 4095, molhado = 0)
  float rainIntensityPct = (1.0F - (rainRaw / 4095.0F)) * 100.0F;
  if (rainIntensityPct < 0.0F) rainIntensityPct = 0.0F;
  bool isRaining = (rainIntensityPct > 15.0F);

  // 6. Lógica Combinacional Local de Segurança: S = (C ∧ B) ∨ A
  checkLocalSafetyLogic(rainIntensityPct, pressure, mqVoltage);

  // Exibição de diagnóstico na Serial
  Serial.printf("Temp: %.1f C | Umid: %.1f %% | Pressao: %.1f hPa\n", temperature, humidity, pressure);
  Serial.printf("Luz: %.1f %% | Chuva: %.1f %% | MQ-135: %.2f V (%s)\n",
                luminosityPct, rainIntensityPct, mqVoltage, isWarmedUp ? "Aquecido" : "Aquecendo");

  // 7. Serialização do Payload JSON Hierárquico via ArduinoJson
  StaticJsonDocument<768> doc;
  doc["device_id"] = DEVICE_ID;
  doc["timestamp"] = (unsigned long)(millis() / 1000);
  doc["wifi_rssi_dbm"] = WiFi.RSSI();

  JsonObject sensorsObj = doc.createNestedObject("sensors");

  JsonObject dhtObj = sensorsObj.createNestedObject("dht22");
  dhtObj["temperature_c"] = round(temperature * 10.0F) / 10.0F;
  dhtObj["humidity_pct"] = round(humidity * 10.0F) / 10.0F;
  dhtObj["status"] = dhtStatus;

  JsonObject bmpObj = sensorsObj.createNestedObject("bmp280");
  bmpObj["temperature_c"] = round(bmpTemp * 10.0F) / 10.0F;
  bmpObj["pressure_hpa"] = round(pressure * 10.0F) / 10.0F;
  bmpObj["altitude_m"] = round(altitude * 10.0F) / 10.0F;
  bmpObj["status"] = bmpStatus;

  JsonObject ldrObj = sensorsObj.createNestedObject("ldr");
  ldrObj["raw_adc"] = ldrRaw;
  ldrObj["luminosity_pct"] = round(luminosityPct * 10.0F) / 10.0F;

  JsonObject mqObj = sensorsObj.createNestedObject("mq135");
  mqObj["raw_adc"] = mqRaw;
  mqObj["voltage_v"] = round(mqVoltage * 100.0F) / 100.0F;
  mqObj["air_quality_ppm"] = round(airQualityPpm * 10.0F) / 10.0F;
  mqObj["is_warmed_up"] = isWarmedUp;

  JsonObject rainObj = sensorsObj.createNestedObject("rain");
  rainObj["raw_adc"] = rainRaw;
  rainObj["intensity_pct"] = round(rainIntensityPct * 10.0F) / 10.0F;
  rainObj["is_raining"] = isRaining;

  String jsonString;
  serializeJson(doc, jsonString);

  // 8. Transmissão HTTP POST para o Backend em Nuvem
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(API_URL);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-API-Key", API_KEY);
    http.setTimeout(10000);

    Serial.println("[HTTP] Transmitindo payload para a API...");
    int httpResponseCode = http.POST(jsonString);

    if (httpResponseCode == 201 || httpResponseCode == 200) {
      Serial.printf("[HTTP] Sucesso! Status Code: %d\n", httpResponseCode);
    } else {
      Serial.printf("[HTTP] Erro na resposta do servidor: %d\n", httpResponseCode);
      String responseBody = http.getString();
      Serial.printf("[HTTP] Detalhes: %s\n", responseBody.c_str());
    }
    http.end();
  } else {
    Serial.println("[HTTP] Ignorado: Sem conexao Wi-Fi no momento.");
  }
}

void checkLocalSafetyLogic(float rainPct, float pressure, float mqVoltage) {
  // C: Chuva Forte (rainPct > 25%)
  bool C = (rainPct > 25.0F);
  // B: Queda Barométrica Crítica (< 1005 hPa)
  bool B = (pressure < 1005.0F);
  // A: Tensão MQ-135 elevada (> 2.5V, indicando alta concentração de gases nocivos)
  bool A = (mqVoltage > 2.5F);

  // Lógica Combinacional: S = (C ∧ B) ∨ A
  bool emergency = (C && B) || A;

  if (emergency) {
    digitalWrite(PIN_ALARM_LED, HIGH);
    Serial.println("[ALARME LOCAL] ALERTA DE EMERGENCIA ATIVADO AUTONOMAMENTE!");
  } else {
    digitalWrite(PIN_ALARM_LED, LOW);
  }
}
