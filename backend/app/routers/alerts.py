from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import AlertRecord
from app.schemas import AlertOut

router = APIRouter(prefix="/api/v1/alerts", tags=["Alertas"])

@router.get("/active", response_model=List[AlertOut])
def get_active_alerts(
    device_id: Optional[str] = Query(None, description="ID da estação"),
    db: Session = Depends(get_db)
):
    """Retorna alertas meteorológicos e civis atualmente ativos (não resolvidos)."""
    query = db.query(AlertRecord).filter(AlertRecord.resolvido_em.is_(None))
    if device_id:
        query = query.filter(AlertRecord.estacao_id == device_id)
    return query.order_by(desc(AlertRecord.emitido_em)).all()

@router.get("/history", response_model=List[AlertOut])
def get_alerts_history(
    device_id: Optional[str] = Query(None, description="ID da estação"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retorna histórico de alertas emitidos."""
    query = db.query(AlertRecord)
    if device_id:
        query = query.filter(AlertRecord.estacao_id == device_id)
    return query.order_by(desc(AlertRecord.emitido_em)).limit(limit).all()
