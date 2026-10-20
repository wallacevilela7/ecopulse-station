from typing import List, Dict, Any, Optional

def evaluate_station_alerts(
    temperature_c: float,
    humidity_pct: float,
    pressure_hpa: float,
    pressure_drop_hpa_per_hour: float,
    air_quality_ppm: float,
    rain_intensity_pct: float,
    is_raining: bool,
    heat_index_c: float
) -> List[Dict[str, str]]:
    """
    Motor de Inferência Lógica para emissão de alertas meteorológicos e civis.
    Aplica os conceitos de Lógica Matemática e Circuitos Lógicos Digitais:
    Variáveis Booleanas:
      C: Chuva severa (rain_intensity_pct > 25.0%)
      B: Queda brusca de pressão barométrica (pressure_drop_hpa_per_hour < -2.0 hPa/h)
      A: Toxicidade atmosférica ou queima de biomassa (air_quality_ppm > 200.0)
    Lógica de Alarme Combinacional: S = (C ∧ B) ∨ A
    """
    alerts = []

    # 1. Regra Combinacional: Alerta de Tempestade Severa (C ∧ B)
    c_chuva = rain_intensity_pct > 25.0
    b_pressao = pressure_drop_hpa_per_hour < -2.0

    if c_chuva and b_pressao:
        alerts.append({
            "tipo_evento": "TEMPESTADE_SEVERA",
            "severidade": "PERIGO",
            "mensagem": "Detecção combinada de precipitação intensa e queda abrupta de pressão barométrica.",
            "recomendacao_cidadao": "Evite transitar por vias com histórico de alagamento. Permaneça em local seguro e coberto."
        })
    elif is_raining and rain_intensity_pct > 50.0:
        alerts.append({
            "tipo_evento": "CHUVA_TORRENCIAL",
            "severidade": "ATENCAO",
            "mensagem": f"Chuva torrencial contínua detectada ({rain_intensity_pct:.1f}% de saturação).",
            "recomendacao_cidadao": "Atenção a rajadas de vento e possíveis quedas de galhos."
        })

    # 2. Regra Atmosférica: Qualidade do Ar Insalubre ou Tóxica (A)
    if air_quality_ppm > 200.0:
        alerts.append({
            "tipo_evento": "AR_INSALUBRE_CRITICO",
            "severidade": "EMERGENCIA",
            "mensagem": f"Concentração perigosa de poluentes/gases redutores ({air_quality_ppm:.1f} PPM).",
            "recomendacao_cidadao": "Mantenha janelas fechadas. Grupos sensíveis, crianças e idosos devem evitar atividades ao ar livre."
        })
    elif air_quality_ppm > 120.0:
        alerts.append({
            "tipo_evento": "AR_DEGRADADO",
            "severidade": "ATENCAO",
            "mensagem": f"Qualidade do ar inadequada para grupos sensíveis ({air_quality_ppm:.1f} PPM).",
            "recomendacao_cidadao": "Hidrate-se com frequência e evite esforços físicos intensos em áreas de tráfego pesado."
        })

    # 3. Regra Biometeorológica: Calor Extremo e Conforto Térmico
    if heat_index_c >= 41.0:
        alerts.append({
            "tipo_evento": "CALOR_EXTREMO_PERIGOSO",
            "severidade": "PERIGO",
            "mensagem": f"Sensação térmica crítica de {heat_index_c:.1f}°C (Risco iminente de insolação e exaustão térmica).",
            "recomendacao_cidadao": "Evite exposição direta ao sol entre 10h e 16h. Beba água regularmente."
        })
    elif heat_index_c >= 36.0:
        alerts.append({
            "tipo_evento": "CALOR_INTENSO",
            "severidade": "ATENCAO",
            "mensagem": f"Sensação térmica elevada de {heat_index_c:.1f}°C.",
            "recomendacao_cidadao": "Aumente a ingestão de líquidos e procure locais arejados."
        })

    # 4. Regra de Umidade Crítica (Ar Seco)
    if humidity_pct < 20.0:
        alerts.append({
            "tipo_evento": "ESTADO_DE_ALERTA_AR_SECO",
            "severidade": "PERIGO",
            "mensagem": f"Umidade relativa do ar em nível crítico ({humidity_pct:.1f}%). Risco elevado de queimadas.",
            "recomendacao_cidadao": "Umidifique ambientes internos com bacias de água ou toalhas úmidas."
        })
    elif humidity_pct < 30.0:
        alerts.append({
            "tipo_evento": "ESTADO_DE_ATENCAO_AR_SECO",
            "severidade": "ATENCAO",
            "mensagem": f"Umidade do ar baixa ({humidity_pct:.1f}%).",
            "recomendacao_cidadao": "Hidratação constante recomendada."
        })

    return alerts
