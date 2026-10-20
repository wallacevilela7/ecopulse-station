from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models import Station
from app.schemas import StationOut, GeometryAnalysisOut
from app.services.geometry import check_coverage_and_distance

router = APIRouter(prefix="/api/v1", tags=["Análise Geoanalítica"])

@router.get("/stations", response_model=List[StationOut])
def list_stations(db: Session = Depends(get_db)):
    """Retorna todas as estações meteorológicas ativas cadastradas."""
    return db.query(Station).filter(Station.ativa == True).all()

@router.get("/analysis/geometry", response_model=GeometryAnalysisOut)
def analyze_user_geometry(
    user_lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude do cidadão"),
    user_lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude do cidadão"),
    device_id: Optional[str] = Query(None, description="ID da estação desejada"),
    db: Session = Depends(get_db)
):
    """
    Aplica a equação canônica da circunferência no plano cartesiano R^2:
    (x - x_0)^2 + (y - y_0)^2 <= r^2
    Calcula a distância euclidiana exata e atesta se o cidadão está na zona de monitoramento direto.
    """
    query = db.query(Station)
    if device_id:
        station = query.filter(Station.id == device_id).first()
    else:
        station = query.first()

    if not station:
        # Fallback para configurações padrão caso ainda não haja dados no banco
        station_id = settings.STATION_ID
        station_name = settings.STATION_NAME
        station_lat = settings.STATION_LAT
        station_lon = settings.STATION_LON
        station_radius = settings.COVERAGE_RADIUS_KM
    else:
        station_id = station.id
        station_name = station.nome
        station_lat = station.latitude
        station_lon = station.longitude
        station_radius = station.raio_cobertura_km

    result = check_coverage_and_distance(
        user_lat=user_lat,
        user_lon=user_lon,
        station_lat=station_lat,
        station_lon=station_lon,
        coverage_radius_km=station_radius
    )

    return GeometryAnalysisOut(
        estacao_id=station_id,
        estacao_nome=station_name,
        station_lat=station_lat,
        station_lon=station_lon,
        user_lat=user_lat,
        user_lon=user_lon,
        distancia_euclidiana_km=result["distancia_euclidiana_km"],
        raio_cobertura_km=station_radius,
        dentro_da_cobertura=result["dentro_da_cobertura"],
        mensagem=result["mensagem"]
    )
