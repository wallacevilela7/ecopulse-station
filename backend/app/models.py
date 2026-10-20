from sqlalchemy import Column, Integer, BigInteger, String, Float, Numeric, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Station(Base):
    __tablename__ = "estacoes"

    id = Column(String(30), primary_key=True)
    nome = Column(String(100), nullable=False)
    cidade = Column(String(80), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=False)
    raio_cobertura_km = Column(Float, default=5.0)
    ativa = Column(Boolean, default=True)
    criada_em = Column(DateTime(timezone=True), server_default=func.now())

    leituras = relationship("SensorReading", back_populates="estacao", cascade="all, delete-orphan")
    alertas = relationship("AlertRecord", back_populates="estacao", cascade="all, delete-orphan")

class SensorReading(Base):
    __tablename__ = "leituras_sensores"

    id = Column(BigInteger, primary_key=True, index=True)
    estacao_id = Column(String(30), ForeignKey("estacoes.id"), index=True)
    data_hora = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Métricas Processadas
    temperatura = Column(Numeric(4, 1), nullable=False)
    umidade = Column(Numeric(4, 1), nullable=False)
    pressao = Column(Numeric(6, 1), nullable=False)
    altitude_m = Column(Numeric(6, 1), nullable=True)
    qualidade_ar = Column(Numeric(6, 1), nullable=False)
    luminosidade = Column(Numeric(5, 1), nullable=False)
    chuva_intensidade = Column(Numeric(5, 1), nullable=False)
    chuva_detectada = Column(Boolean, default=False)
    sensacao_termica = Column(Numeric(4, 1), nullable=True)
    aqi_classificacao = Column(String(30), nullable=True)

    # Diagnóstico e Valores Brutos do ADC (12 bits)
    wifi_rssi_dbm = Column(Integer, nullable=True)
    ldr_raw_adc = Column(Integer, nullable=True)
    mq135_raw_adc = Column(Integer, nullable=True)
    mq135_voltage_v = Column(Numeric(4, 2), nullable=True)
    mq135_warmed_up = Column(Boolean, default=True)
    rain_raw_adc = Column(Integer, nullable=True)
    dht22_status = Column(String(15), default="OK")
    bmp280_status = Column(String(15), default="OK")

    estacao = relationship("Station", back_populates="leituras")

class AlertRecord(Base):
    __tablename__ = "alertas_emitidos"

    id = Column(BigInteger, primary_key=True, index=True)
    estacao_id = Column(String(30), ForeignKey("estacoes.id"), index=True)
    tipo_evento = Column(String(50), nullable=False)
    severidade = Column(String(20), nullable=False)
    mensagem = Column(Text, nullable=False)
    recomendacao_cidadao = Column(Text, nullable=False)
    emitido_em = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    resolvido_em = Column(DateTime(timezone=True), nullable=True)

    estacao = relationship("Station", back_populates="alertas")
