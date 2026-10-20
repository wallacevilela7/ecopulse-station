import math
from typing import Tuple, Dict, Any

EARTH_RADIUS_KM = 6371.0

def calculate_local_plane_coordinates(
    lat: float,
    lon: float,
    origin_lat: float,
    origin_lon: float
) -> Tuple[float, float]:
    """
    Projeta coordenadas geodésicas (Latitude, Longitude) no plano cartesiano R^2 tangente local
    através da projeção equirretangular local.
    Retorna as coordenadas (x, y) em quilômetros em relação à origem da estação (0, 0).
    """
    phi = math.radians(lat)
    lambda_val = math.radians(lon)
    phi_0 = math.radians(origin_lat)
    lambda_0 = math.radians(origin_lon)

    # Coordenadas no plano cartesiano
    x = EARTH_RADIUS_KM * (lambda_val - lambda_0) * math.cos((phi + phi_0) / 2.0)
    y = EARTH_RADIUS_KM * (phi - phi_0)

    return round(x, 4), round(y, 4)

def check_coverage_and_distance(
    user_lat: float,
    user_lon: float,
    station_lat: float,
    station_lon: float,
    coverage_radius_km: float
) -> Dict[str, Any]:
    """
    Aplica a equação canônica da circunferência no plano cartesiano:
    (x - x_0)^2 + (y - y_0)^2 <= r^2
    Para verificar se o usuário está dentro da área analítica de abrangência dos alertas.
    """
    x, y = calculate_local_plane_coordinates(user_lat, user_lon, station_lat, station_lon)

    # Distância Euclidiana em relação à origem da estação (0, 0)
    distancia_euclidiana = math.sqrt(x**2 + y**2)
    distancia_arredondada = round(distancia_euclidiana, 2)

    # Inequação da circunferência canônica
    dentro_do_raio = distancia_euclidiana <= coverage_radius_km

    if dentro_do_raio:
        mensagem = (
            f"Você está a {distancia_arredondada} km da estação, plenamente DENTRO da zona de cobertura direta "
            f"analítica ({coverage_radius_km} km). Alertas e microclima locais aplicam-se a você."
        )
    else:
        mensagem = (
            f"Você está a {distancia_arredondada} km da estação, FORA do raio analítico principal de "
            f"{coverage_radius_km} km. Os dados são representativos para a macrorregião urbana."
        )

    return {
        "x_km": x,
        "y_km": y,
        "distancia_euclidiana_km": distancia_arredondada,
        "dentro_da_cobertura": dentro_do_raio,
        "mensagem": mensagem
    }
