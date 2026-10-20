# EcoPulse Station - Firmware ESP32

Código embarcado em C++ (Arduino Framework / PlatformIO) para coleta de dados climáticos e transmissão em tempo real para a nuvem.

## Sensores e Periféricos Integrados
- **DHT22**: GPIO 4 (One-Wire Digital)
- **BMP280**: GPIO 21 (SDA) e GPIO 22 (SCL)
- **LDR**: GPIO 34 (ADC1 com divisor pull-down de 10kΩ)
- **Sensor de Chuva**: GPIO 35 (ADC1 alimentado em 3.3V)
- **MQ-135**: GPIO 32 (ADC1 com atenuador resistivo 1kΩ / 2kΩ e aquecedor em 5V)
- **Alarme Local**: GPIO 25 (LED/Buzzer acionado por $S = (C \land B) \lor A$)
- **Status Wi-Fi**: GPIO 26 (LED indicador de conectividade)

## Como Compilar e Gravar
1. Copie o arquivo `include/config.h.example` para `include/config.h`:
   ```bash
   cp include/config.h.example include/config.h
   ```
2. Abra `include/config.h` e configure seu SSID, senha de Wi-Fi e endereço IP do backend.
3. Conecte o ESP32 via cabo micro-USB / Type-C.
4. Grave utilizando o **PlatformIO**:
   ```bash
   pio run --target upload
   pio device monitor
   ```
   Ou através da **Arduino IDE** abrindo `src/main.cpp`.
