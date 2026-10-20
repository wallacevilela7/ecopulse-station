# 🌱 EcoPulse Station &bull; Estação Meteorológica Inteligente

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![ESP32](https://img.shields.io/badge/Hardware-ESP32-E7352C?style=for-the-badge&logo=espressif&logoColor=white)](https://www.espressif.com)
[![Docker](https://img.shields.io/badge/Deploy-Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

> **Projeto e Desenvolvimento II (PD-II / PIM II)**  
> **Curso:** Bacharelado em Ciência da Computação (2º Semestre) &bull; **Universidade Paulista (UNIP)**  
> **Tema:** Cidades Inteligentes, Internet das Coisas (IoT), Sustentabilidade e Transparência Socioambiental.

---

## 📋 Visão Geral do Projeto

O **EcoPulse Station** é uma solução completa *end-to-end* de **Internet das Coisas (IoT)** e **Computação em Nuvem** desenvolvida para coletar, processar e disseminar métricas microclimáticas e de qualidade do ar urbano em tempo real.

A solução integra um dispositivo microcontrolado **ESP32** com múltiplos sensores analógicos e digitais, uma API REST de alta performance construída em **FastAPI (Python)**, persistência relacional com séries temporais em **PostgreSQL**, e um **Dashboard Web Público** interativo com gráficos e mapas geoanalíticos.

```
+---------------------------------------------------------------------------------+
| CAMADA 1: EMBARCADO (ESP32 C++)                                                 |
| Sensores: DHT22, BMP280, MQ-135, LDR, Placa de Chuva, Alarme Local (GPIO 25)    |
+---------------------------------------+-----------------------------------------+
                                        |  HTTP/1.1 POST /api/v1/telemetry (Wi-Fi)
                                        v
+---------------------------------------------------------------------------------+
| CAMADA 2: BACKEND & INFRAESTRUTURA (AWS EC2 / Python FastAPI / Docker)          |
| Ingestão, validação Pydantic, cálculo de Sensação Térmica e Geometria           |
+---------------------------------------+-----------------------------------------+
                                        |  SQLAlchemy ORM (Conexão SSL)
                                        v
+---------------------------------------------------------------------------------+
| CAMADA 3: BANCO DE DADOS EM NUVEM (PostgreSQL 16)                               |
| Séries temporais de leituras (processadas e brutas ADC) e tabela de alertas     |
+---------------------------------------+-----------------------------------------+
                                        |  REST API / JSON
                                        v
+---------------------------------------------------------------------------------+
| CAMADA 4: DASHBOARD WEB PÚBLICO (HTML5 / Vanilla CSS / Chart.js / Leaflet.js)   |
| Métricas em tempo real, séries temporais de 24h e raio analítico da estação     |
+---------------------------------------------------------------------------------+
```

---

## 📁 Estrutura da Codebase

```
ecopulse-station/
├── .gitignore
├── docker-compose.yml          # Orquestração local de PostgreSQL e Backend API
├── LICENSE                     # Licença MIT
├── README.md                   # Documentação principal do repositório
│
├── backend/                    # Camada de API, Regras de Negócio e Infraestrutura
│   ├── .env.example            # Variáveis de ambiente de referência
│   ├── requirements.txt        # Dependências Python (FastAPI, SQLAlchemy, Pydantic)
│   ├── app/
│   │   ├── main.py             # Entrada da API FastAPI, CORS e Healthcheck
│   │   ├── config.py           # Gestão tipada de configurações com pydantic-settings
│   │   ├── database.py         # Sessão e engine SQLAlchemy
│   │   ├── models.py           # Modelos relacionais (Station, SensorReading, AlertRecord)
│   │   ├── schemas.py          # Schemas Pydantic v2 para requisições e respostas
│   │   ├── services/
│   │   │   ├── weather_math.py # Fórmulas (Rothfusz Heat Index, AQI, Ponto de Orvalho)
│   │   │   ├── alert_engine.py # Inferência lógica baseada em regras combinacionais
│   │   │   └── geometry.py     # Equação da circunferência e distância euclidiana
│   │   └── routers/
│   │       ├── telemetry.py    # POST /api/v1/telemetry, GET latest & history
│   │       ├── alerts.py       # GET /api/v1/alerts/active & history
│   │       └── analysis.py     # GET /api/v1/analysis/geometry & stations
│   ├── infra/                  # Infraestrutura como Código, Banco e Deploy
│   │   ├── database/
│   │   │   ├── 01_init.sql     # DDL oficial PostgreSQL (com campos raw do ADC)
│   │   │   └── seed.sql        # Dados semente para testes rápidos
│   │   ├── docker/
│   │   │   ├── Dockerfile      # Imagem Docker otimizada Python 3.12-slim
│   │   │   └── nginx.conf      # Configuração de proxy reverso Nginx com Gzip
│   │   └── deploy/
│   │       ├── setup_ec2.sh    # Script de provisionamento em instância AWS EC2
│   │       └── ecopulse-backend.service # Unidade Systemd para produção
│   └── tests/                  # Testes unitários automatizados (pytest)
│       └── test_math.py
│
├── frontend/                   # Dashboard Web Público
│   ├── index.html              # Interface web semântica responsiva
│   ├── css/styles.css          # Design system moderno com tokens e Dark/Light mode
│   ├── js/
│   │   ├── app.js              # Controlador principal e polling assíncrono
│   │   ├── charts.js           # Gráficos dinâmicos com Chart.js
│   │   └── map.js              # Mapa interativo e raio de cobertura com Leaflet.js
│   └── README.md
│
├── firmware/                   # Código Embarcado do Microcontrolador (C++)
│   ├── platformio.ini          # Configuração PlatformIO para ESP32 DevKit v1
│   ├── include/config.h.example # Chaves de Wi-Fi, API URL e pinagem
│   ├── src/main.cpp            # Firmware C++ completo (leitura, JSON e envio HTTP)
│   └── README.md
│
└── docs/                       # Especificação Técnica e Diagramas
    ├── especificacao_tecnica.md # Especificação acadêmica ABNT completa
    ├── index.html              # Portal estático de consulta da documentação
    └── assets/
        └── protoboard_esquematico.jpg # Diagrama oficial de montagem da protoboard dupla
```

---

## ⚡ Como Executar o Projeto

### Pré-requisitos
- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/) **OU** Python 3.12+ e PostgreSQL 15+.

### 1. Inicialização Rápida com Docker (Recomendado)
Para subir o banco de dados PostgreSQL e a API FastAPI com um único comando:

```bash
# Clone o repositório
git clone https://github.com/wallacevilela7/ecopulse-station.git
cd ecopulse-station

# Suba os containers
docker compose up -d
```
- A API estará disponível em: [http://localhost:8000](http://localhost:8000)
- Documentação Swagger interativa: [http://localhost:8000/docs](http://localhost:8000/docs)
- Verificação de saúde: [http://localhost:8000/health](http://localhost:8000/health)

### 2. Executando o Backend Localmente (Sem Docker)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Executar a aplicação
uvicorn app.main:app --reload --port 8000

# Executar os testes unitários
pytest tests/ -v
```

### 3. Executando o Frontend Web
Basta abrir `frontend/index.html` em qualquer navegador ou rodar um servidor web estático:
```bash
cd frontend
python3 -m http.server 3000
```
Acesse [http://localhost:3000](http://localhost:3000).

---

## 🔌 Hardware e Conexões (ESP32)

A montagem física utiliza duas protoboards unidas lado a lado para segregação dos barramentos de alimentação:

| Sensor / Periférico | Interface | Conexão ESP32 | Condicionamento Elétrico |
| :--- | :--- | :--- | :--- |
| **BMP280** | I2C Digital | GPIO 21 (SDA) / GPIO 22 (SCL) | VCC ligado a 3.3V / GND comum |
| **DHT22** | One-Wire Digital | GPIO 4 | Pull-up de 10kΩ entre VCC e DATA |
| **LDR** | Analógica (ADC1) | GPIO 34 | Divisor de tensão com resistor pull-down 10kΩ ao GND |
| **Sensor de Chuva** | Analógica (ADC1) | GPIO 35 | Alimentado em 3.3V (saída de 0V a 3.3V) |
| **MQ-135** | Analógica (ADC1) | GPIO 32 | Aquecedor em 5V (VIN); divisor de proteção (1kΩ/2kΩ) atenua 5V para ~3.33V |
| **Alarme Autônomo**| Saída Digital | GPIO 25 | Acionamento de buzzer/LED por lógica combinacional |

---

## 📡 Contrato de Telemetria (API REST)

O ESP32 envia medições periódicas via `POST /api/v1/telemetry`:

* **Header:** `X-API-Key: secreto_pim2_unip_2026`
* **Content-Type:** `application/json`

```json
{
  "device_id": "esp32-meteo-01",
  "timestamp": 1792508580,
  "wifi_rssi_dbm": -62,
  "sensors": {
    "dht22": {
      "temperature_c": 25.4,
      "humidity_pct": 68.2,
      "status": "OK"
    },
    "bmp280": {
      "temperature_c": 25.6,
      "pressure_hpa": 1013.25,
      "altitude_m": 760.5,
      "status": "OK"
    },
    "ldr": {
      "raw_adc": 2890,
      "luminosity_pct": 70.6
    },
    "mq135": {
      "raw_adc": 1150,
      "voltage_v": 1.39,
      "air_quality_ppm": 415.8,
      "is_warmed_up": true
    },
    "rain": {
      "raw_adc": 3850,
      "intensity_pct": 6.0,
      "is_raining": false
    }
  }
}
```

---

## 🎓 Alinhamento com a Grade Curricular da UNIP (2º Semestre)

| Disciplina Curricular | Aplicação Concreta na Codebase |
| :--- | :--- |
| **Circuitos Lógicos Digitais** | Dimensionamento dos divisores de tensão (LDR e MQ-135) e circuito local autônomo acionado pela expressão $S = (C \land B) \lor A$. |
| **Lógica Matemática** | Modelagem das tabelas-verdade de alerta civil e regras de inferência booleana implementadas em `alert_engine.py`. |
| **Programação Estruturada em Python** | Arquitetura modular da API FastAPI, tipagem estática com Pydantic e persistência relacional com SQLAlchemy. |
| **Geometria Analítica para Computação** | Projeção em plano tangente local, inequação canônica da circunferência $(x-x_0)^2 + (y-y_0)^2 \le r^2$ e cálculo da distância euclidiana do usuário. |
| **Educação Ambiental** | Monitoramento de qualidade do ar e indicadores biometeorológicos abertos à comunidade no dashboard público. |

---

## 👥 Autores
- **Wallace Vilela** ([@wallacevilela7](https://github.com/wallacevilela7))
- Bacharelado em Ciência da Computação &bull; Universidade Paulista (UNIP)
