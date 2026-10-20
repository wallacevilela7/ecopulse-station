import pytest
from app.services.weather_math import calculate_heat_index, classify_aqi, calculate_dew_point
from app.services.geometry import calculate_local_plane_coordinates, check_coverage_and_distance
from app.services.alert_engine import evaluate_station_alerts

def test_heat_index_low_temperature():
    # Temperaturas menores que 20°C retornam a própria temperatura
    assert calculate_heat_index(18.0, 50.0) == 18.0

def test_heat_index_hot_and_humid():
    # 32°C com 70% de umidade resulta em sensação térmica alta (> 38°C)
    hi = calculate_heat_index(32.0, 70.0)
    assert hi > 38.0

def test_aqi_classification():
    assert classify_aqi(35.0) == "Boa"
    assert classify_aqi(80.0) == "Moderada"
    assert classify_aqi(140.0) == "Inadequada"
    assert classify_aqi(180.0) == "Má"
    assert classify_aqi(250.0) == "Muito Má"
    assert classify_aqi(350.0) == "Crítica"

def test_dew_point():
    dp = calculate_dew_point(25.0, 60.0)
    assert 15.0 <= dp <= 18.0

def test_geometry_same_point():
    lat = -23.550520
    lon = -46.633308
    res = check_coverage_and_distance(lat, lon, lat, lon, 5.0)
    assert res["distancia_euclidiana_km"] == 0.0
    assert res["dentro_da_cobertura"] is True

def test_geometry_outside_coverage():
    # Ponto distante (> 20 km)
    station_lat = -23.550520
    station_lon = -46.633308
    user_lat = -23.750520
    user_lon = -46.833308
    res = check_coverage_and_distance(user_lat, user_lon, station_lat, station_lon, 5.0)
    assert res["distancia_euclidiana_km"] > 5.0
    assert res["dentro_da_cobertura"] is False

def test_alert_engine_storm_trigger():
    # C and B combination: Rain > 25% and Pressure Drop < -2.0
    alerts = evaluate_station_alerts(
        temperature_c=24.0,
        humidity_pct=85.0,
        pressure_hpa=998.0,
        pressure_drop_hpa_per_hour=-3.5,
        air_quality_ppm=45.0,
        rain_intensity_pct=60.0,
        is_raining=True,
        heat_index_c=24.0
    )
    event_types = [a["tipo_evento"] for a in alerts]
    assert "TEMPESTADE_SEVERA" in event_types
