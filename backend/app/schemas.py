from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

# ==============================================================
# Modelos de Ingestão de Telemetria (ESP32 -> Backend)
# ==============================================================

class DHT22Data(BaseModel):
    temperature_c: float = Field(..., ge=-40.0, le=80.0, description="Temperatura em graus Celsius")
    humidity_pct: float = Field(..., ge=0.0, le=100.0, description="Umidade relativa do ar (%)")
    status: str = Field(default="OK")

class BMP280Data(BaseModel):
    temperature_c: float
    pressure_hpa: float = Field(..., ge=300.0, le=1100.0, description="Pressão atmosférica em hPa")
    altitude_m: float
    status: str = Field(default="OK")

class LDRData(BaseModel):
    raw_adc: int = Field(..., ge=0, le=4095, description="Valor bruto do ADC (12 bits)")
    luminosity_pct: float = Field(..., ge=0.0, le=100.0, description="Luminosidade percentual")

class MQ135Data(BaseModel):
    raw_adc: int = Field(..., ge=0, le=4095, description="Valor bruto do ADC (12 bits)")
    voltage_v: float = Field(..., ge=0.0, le=5.0, description="Tensão reconstituída do sensor")
    air_quality_ppm: float = Field(..., description="Estimativa de partículas/gases em PPM")
    is_warmed_up: bool = Field(default=True, description="Indica se o sensor completou 3 min de aquecimento")

class RainData(BaseModel):
    raw_adc: int = Field(..., ge=0, le=4095, description="Valor bruto do ADC (12 bits)")
    intensity_pct: float = Field(..., ge=0.0, le=100.0, description="Intensidade de chuva calculada")
    is_raining: bool = Field(..., description="Flag booleana indicando presença de chuva")

class SensorsPayload(BaseModel):
    dht22: DHT22Data
    bmp280: BMP280Data
    ldr: LDRData
    mq135: MQ135Data
    rain: RainData

class TelemetryIngest(BaseModel):
    device_id: str = Field(..., min_length=3, max_length=50, description="Identificador único da estação")
    timestamp: Optional[int] = Field(None, description="Unix timestamp UTC")
    wifi_rssi_dbm: Optional[int] = Field(None, ge=-120, le=0, description="Sinal Wi-Fi em dBm")
    sensors: SensorsPayload

# ==============================================================
# Modelos de Resposta para Frontend e Clientes REST
# ==============================================================

class SensorReadingOut(BaseModel):
    id: int
    estacao_id: str
    data_hora: datetime
    temperatura: float
    umidade: float
    pressao: float
    altitude_m: Optional[float] = None
    qualidade_ar: float
    luminosidade: float
    chuva_intensidade: float
    chuva_detectada: bool
    sensacao_termica: Optional[float] = None
    aqi_classificacao: Optional[str] = None
    wifi_rssi_dbm: Optional[int] = None

    class Config:
        from_attributes = True

class AlertOut(BaseModel):
    id: int
    estacao_id: str
    tipo_evento: str
    severidade: str
    mensagem: str
    recomendacao_cidadao: str
    emitido_em: datetime
    resolvido_em: Optional[datetime] = None

    class Config:
        from_attributes = True

class StationOut(BaseModel):
    id: str
    nome: str
    cidade: str
    latitude: float
    longitude: float
    altitude: float
    raio_cobertura_km: float
    ativa: bool

    class Config:
        from_attributes = True

class GeometryAnalysisOut(BaseModel):
    estacao_id: str
    estacao_nome: str
    station_lat: float
    station_lon: float
    user_lat: float
    user_lon: float
    distancia_euclidiana_km: float
    raio_cobertura_km: float
    dentro_da_cobertura: bool
    mensagem: str
