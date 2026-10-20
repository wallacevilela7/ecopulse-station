-- ==============================================================
-- EcoPulse Station - DDL Oficial de Inicialização do PostgreSQL
-- Projeto e Desenvolvimento II (PIM II - Ciência da Computação UNIP)
-- ==============================================================

-- 1. Tabela de Cadastro das Estações Meteorológicas
CREATE TABLE IF NOT EXISTS estacoes (
    id VARCHAR(30) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cidade VARCHAR(80) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    altitude DOUBLE PRECISION NOT NULL,
    raio_cobertura_km DOUBLE PRECISION DEFAULT 5.0,
    ativa BOOLEAN DEFAULT TRUE,
    criada_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabela de Séries Temporais das Leituras dos Sensores
CREATE TABLE IF NOT EXISTS leituras_sensores (
    id BIGSERIAL PRIMARY KEY,
    estacao_id VARCHAR(30) REFERENCES estacoes(id),
    data_hora TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Métricas meteorológicas processadas
    temperatura NUMERIC(4, 1) NOT NULL,
    umidade NUMERIC(4, 1) NOT NULL,
    pressao NUMERIC(6, 1) NOT NULL,
    altitude_m NUMERIC(6, 1),
    qualidade_ar NUMERIC(6, 1) NOT NULL,
    luminosidade NUMERIC(5, 1) NOT NULL,
    chuva_intensidade NUMERIC(5, 1) NOT NULL,
    chuva_detectada BOOLEAN DEFAULT FALSE,
    sensacao_termica NUMERIC(4, 1),
    aqi_classificacao VARCHAR(30),
    -- Diagnóstico e valores brutos do conversor analógico-digital (ADC 12 bits)
    wifi_rssi_dbm INTEGER,
    ldr_raw_adc INTEGER,
    mq135_raw_adc INTEGER,
    mq135_voltage_v NUMERIC(4, 2),
    mq135_warmed_up BOOLEAN DEFAULT TRUE,
    rain_raw_adc INTEGER,
    dht22_status VARCHAR(15) DEFAULT 'OK',
    bmp280_status VARCHAR(15) DEFAULT 'OK'
);

-- Índice composto para consultas temporais ultra-rápidas no Dashboard
CREATE INDEX IF NOT EXISTS idx_leituras_estacao_data ON leituras_sensores (estacao_id, data_hora DESC);

-- 3. Tabela de Alertas e Notificações Emitidas
CREATE TABLE IF NOT EXISTS alertas_emitidos (
    id BIGSERIAL PRIMARY KEY,
    estacao_id VARCHAR(30) REFERENCES estacoes(id),
    tipo_evento VARCHAR(50) NOT NULL,      -- 'TEMPESTADE', 'AR_INSALUBRE', 'CALOR_EXTREMO'
    severidade VARCHAR(20) NOT NULL,       -- 'INFO', 'ATENCAO', 'PERIGO', 'EMERGENCIA'
    mensagem TEXT NOT NULL,
    recomendacao_cidadao TEXT NOT NULL,
    emitido_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolvido_em TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_alertas_ativos ON alertas_emitidos (estacao_id, emitido_em DESC) WHERE resolvido_em IS NULL;
