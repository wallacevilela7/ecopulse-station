from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import engine, Base
from app.routers import telemetry, alerts, analysis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização: cria tabelas se ainda não existirem (fallback leve para dev)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[Aviso BD] Inicialização de tabelas adiada: {e}")
    yield

app = FastAPI(
    title="EcoPulse Station API",
    description=(
        "API REST de Ingestão de Telemetria e Monitoramento Climático Urbano. "
        "Desenvolvido para o Projeto Integrado Multidisciplinar II (PIM II / PD-II) - "
        "Ciência da Computação UNIP."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS para permitir acesso do Dashboard Web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão dos Routers
app.include_router(telemetry.router)
app.include_router(alerts.router)
app.include_router(analysis.router)

@app.get("/health", tags=["Saúde"])
def health_check():
    """Endpoint de verificação de disponibilidade da aplicação e conexão com banco."""
    db_status = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "database": db_status,
        "environment": settings.ENV,
        "station_id": settings.STATION_ID
    }
