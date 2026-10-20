import math

def calculate_heat_index(temperature_c: float, humidity_pct: float) -> float:
    """
    Calcula a sensação térmica (Heat Index) através do modelo polinomial de Rothfusz (NOAA/NWS).
    Retorna a sensação térmica equivalente em graus Celsius.
    """
    if temperature_c < 20.0:
        return round(temperature_c, 1)

    # Conversão para Fahrenheit para aplicação da fórmula padrão NOAA
    T = (temperature_c * 9.0 / 5.0) + 32.0
    R = humidity_pct

    # Aproximação simplificada inicial
    hi = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (R * 0.094))

    # Se a sensação passar de 80°F, aplica o polinômio completo de 9 constantes
    if hi >= 80.0:
        c1 = -42.379
        c2 = 2.04901523
        c3 = 10.14333127
        c4 = -0.22475541
        c5 = -0.00683783
        c6 = -0.05481717
        c7 = 0.00122874
        c8 = 0.00085282
        c9 = -0.00000199

        hi = (c1 + (c2 * T) + (c3 * R) + (c4 * T * R) +
              (c5 * (T ** 2)) + (c6 * (R ** 2)) +
              (c7 * (T ** 2) * R) + (c8 * T * (R ** 2)) +
              (c9 * (T ** 2) * (R ** 2)))

        # Ajuste de baixa umidade
        if R < 13.0 and 80.0 <= T <= 112.0:
            adj = ((13.0 - R) / 4.0) * math.sqrt((17.0 - abs(T - 95.0)) / 17.0)
            hi -= adj
        # Ajuste de alta umidade
        elif R > 85.0 and 80.0 <= T <= 87.0:
            adj = ((R - 85.0) / 10.0) * ((87.0 - T) / 5.0)
            hi += adj

    # Converte de volta para Celsius
    hi_c = (hi - 32.0) * 5.0 / 9.0
    return round(hi_c, 1)

def classify_aqi(ppm: float) -> str:
    """
    Classifica a qualidade do ar conforme as faixas padronizadas (OMS / CETESB).
    """
    if ppm <= 50.0:
        return "Boa"
    elif ppm <= 100.0:
        return "Moderada"
    elif ppm <= 150.0:
        return "Inadequada"
    elif ppm <= 200.0:
        return "Má"
    elif ppm <= 300.0:
        return "Muito Má"
    else:
        return "Crítica"

def calculate_dew_point(temperature_c: float, humidity_pct: float) -> float:
    """
    Calcula o ponto de orvalho (Dew Point) via aproximação de Magnus-Tetens.
    """
    a = 17.27
    b = 237.7
    alpha = ((a * temperature_c) / (b + temperature_c)) + math.log(max(humidity_pct, 1.0) / 100.0)
    dew_point = (b * alpha) / (a - alpha)
    return round(dew_point, 1)
