import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "development"
    API_KEY: str = "secreto_pim2_unip_2026"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ecopulse_db"
    
    # Metadados e Localização da Estação Padrão
    STATION_ID: str = "esp32-meteo-01"
    STATION_NAME: str = "Estação Meteorológica UNIP - Campus Central"
    STATION_CITY: str = "São Paulo"
    STATION_LAT: float = -23.550520
    STATION_LON: float = -46.633308
    STATION_ALTITUDE: float = 760.0
    COVERAGE_RADIUS_KM: float = 5.0

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
