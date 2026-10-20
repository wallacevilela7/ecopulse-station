-- ==============================================================
-- EcoPulse Station - Seed Data Inicial
-- ==============================================================

-- Inserir Estação Padrão
INSERT INTO estacoes (id, nome, cidade, latitude, longitude, altitude, raio_cobertura_km, ativa)
VALUES (
    'esp32-meteo-01',
    'Estação Piloto UNIP - Smart Cities',
    'São Paulo',
    -23.550520,
    -46.633308,
    760.0,
    5.0,
    TRUE
)
ON CONFLICT (id) DO NOTHING;

-- Inserir Leitura Inicial de Referência
INSERT INTO leituras_sensores (
    estacao_id,
    temperatura,
    umidade,
    pressao,
    altitude_m,
    qualidade_ar,
    luminosidade,
    chuva_intensidade,
    chuva_detectada,
    sensacao_termica,
    aqi_classificacao,
    wifi_rssi_dbm,
    ldr_raw_adc,
    mq135_raw_adc,
    mq135_voltage_v,
    mq135_warmed_up,
    rain_raw_adc,
    dht22_status,
    bmp280_status
)
VALUES (
    'esp32-meteo-01',
    25.5,
    65.0,
    1013.2,
    760.5,
    65.0,
    75.0,
    0.0,
    FALSE,
    26.0,
    'Moderada',
    -62,
    3072,
    1150,
    1.39,
    TRUE,
    4000,
    'OK',
    'OK'
);
