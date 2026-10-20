from typing import List, Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Header, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.config import settings
from app.models import Station, SensorReading, AlertRecord
from app.schemas import TelemetryIngest, SensorReadingOut
from app.services.weather_math import calculate_heat_index, classify_aqi
from app.services.alert_engine import evaluate_station_alerts

router = APIRouter(prefix="/api/v1", tags=["Telemetria"])

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Valida o cabeçalho X-API-Key enviado pelo microcontrolador ESP32."""
    if not x_api_key or x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação falhou: chave X-API-Key inválida ou não fornecida."
        )
    return x_api_key

@router.post("/telemetry", status_code=status.HTTP_201_CREATED, response_model=SensorReadingOut)
@router.post("/telemetria", status_code=status.HTTP_201_CREATED, response_model=SensorReadingOut, include_in_schema=False)
def ingest_telemetry(
    payload: TelemetryIngest,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
):
    """
    Ingestão canônica de telemetria enviada pelo ESP32.
    - Valida o payload Pydantic
    - Calcula sensação térmica (Rothfusz Heat Index) e índice AQI
    - Avalia motor de alertas combinacionais
    - Persiste leitura no PostgreSQL
    """
    # 1. Garante a existência do registro da estação
    station = db.query(Station).filter(Station.id == payload.device_id).first()
    if not station:
        station = Station(
            id=payload.device_id,
            nome=settings.STATION_NAME,
            cidade=settings.STATION_CITY,
            latitude=settings.STATION_LAT,
            longitude=settings.STATION_LON,
            altitude=settings.STATION_ALTITUDE,
            raio_cobertura_km=settings.COVERAGE_RADIUS_KM
        )
        db.add(station)
        db.commit()
        db.refresh(station)

    # 2. Extrai dados dos sensores
    sensors = payload.sensors
    dht = sensors.dht22
    bmp = sensors.bmp280
    ldr = sensors.ldr
    mq = sensors.mq135
    rain = sensors.rain

    # 3. Calcula métricas derivadas
    heat_index = calculate_heat_index(dht.temperature_c, dht.humidity_pct)
    aqi_desc = classify_aqi(mq.air_quality_ppm)

    # 4. Avalia taxa de variação barométrica com base na leitura anterior
    last_reading = (
        db.query(SensorReading)
        .filter(SensorReading.estacao_id == payload.device_id)
        .order_by(desc(SensorReading.data_hora))
        .first()
    )

    pressure_drop = 0.0
    if last_reading and last_reading.data_hora:
        time_diff = (datetime.now(timezone.utc) - last_reading.data_hora.replace(tzinfo=timezone.utc)).total_seconds() / 3600.0
        if time_diff > 0:
            pressure_drop = (float(bmp.pressure_hpa) - float(last_reading.pressao)) / time_diff

    # 5. Avalia regras lógicas de alerta
    alerts_triggered = evaluate_station_alerts(
        temperature_c=dht.temperature_c,
        humidity_pct=dht.humidity_pct,
        pressure_hpa=bmp.pressure_hpa,
        pressure_drop_hpa_per_hour=pressure_drop,
        air_quality_ppm=mq.air_quality_ppm,
        rain_intensity_pct=rain.intensity_pct,
        is_raining=rain.is_raining,
        heat_index_c=heat_index
    )

    for alert in alerts_triggered:
        new_alert = AlertRecord(
            estacao_id=payload.device_id,
            tipo_evento=alert["tipo_evento"],
            severidade=alert["severidade"],
            mensagem=alert["mensagem"],
            recomendacao_cidadao=alert["recomendacao_cidadao"]
        )
        db.add(new_alert)

    # 6. Cria registro de leitura
    new_reading = SensorReading(
        estacao_id=payload.device_id,
        temperatura=dht.temperature_c,
        umidade=dht.humidity_pct,
        pressao=bmp.pressure_hpa,
        altitude_m=bmp.altitude_m,
        qualidade_ar=mq.air_quality_ppm,
        luminosidade=ldr.luminosity_pct,
        chuva_intensidade=rain.intensity_pct,
        chuva_detectada=rain.is_raining,
        sensacao_termica=heat_index,
        aqi_classificacao=aqi_desc,
        wifi_rssi_dbm=payload.wifi_rssi_dbm,
        ldr_raw_adc=ldr.raw_adc,
        mq135_raw_adc=mq.raw_adc,
        mq135_voltage_v=mq.voltage_v,
        mq135_warmed_up=mq.is_warmed_up,
        rain_raw_adc=rain.raw_adc,
        dht22_status=dht.status,
        bmp280_status=bmp.status
    )

    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)

    return new_reading

@router.get("/telemetry/latest", response_model=SensorReadingOut)
@router.get("/telemetria/atual", response_model=SensorReadingOut, include_in_schema=False)
def get_latest_telemetry(
    device_id: Optional[str] = Query(None, description="ID da estação"),
    db: Session = Depends(get_db)
):
    """Retorna a medição meteorológica mais recente para exibição no dashboard."""
    query = db.query(SensorReading)
    if device_id:
        query = query.filter(SensorReading.estacao_id == device_id)
    
    latest = query.order_by(desc(SensorReading.data_hora)).first()
    if not latest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma medição encontrada.")
    return latest

@router.get("/telemetry/history", response_model=List[SensorReadingOut])
@router.get("/telemetria/historico", response_model=List[SensorReadingOut], include_in_schema=False)
def get_telemetry_history(
    device_id: Optional[str] = Query(None, description="ID da estação"),
    hours: int = Query(24, ge=1, le=168, description="Janela de tempo em horas"),
    limit: int = Query(100, ge=1, le=500, description="Limite máximo de pontos"),
    db: Session = Depends(get_db)
):
    """Retorna o histórico cronológico de leituras para montagem dos gráficos no Chart.js."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    query = db.query(SensorReading).filter(SensorReading.data_hora >= cutoff)

    if device_id:
        query = query.filter(SensorReading.estacao_id == device_id)

    readings = query.order_by(SensorReading.data_hora.asc()).limit(limit).all()
    return readings
