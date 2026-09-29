from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import engine, Base
from app.routes import products, prices, alerts

# Création automatique des tables SQLite / PostgreSQL au démarrage
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PriceWatch API",
    description="API de surveillance et comparaison de prix multi-sites (Projet L3 MIAGE - Université de Toulouse).",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Activation de CORS pour permettre les requêtes frontend éventuelles
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes de l'API
app.include_router(products.router, prefix="/api")
app.include_router(prices.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")

# On inclut également les routes sans préfixe pour respecter fidèlement les endpoints spécifiés (/products, /scrape, /alerts...)
app.include_router(products.router, include_in_schema=False)
app.include_router(prices.router, include_in_schema=False)
app.include_router(alerts.router, include_in_schema=False)

BASE_DIR = Path(__file__).resolve().parent.parent

# Montage des dossiers statiques
static_dir = BASE_DIR / "app" / "static"
demo_dir = BASE_DIR / "demo_sites"

if demo_dir.is_dir():
    app.mount("/demo", StaticFiles(directory=str(demo_dir)), name="demo")

if static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", include_in_schema=False)
def serve_index():
    """Sert l'interface web utilisateur PriceWatch."""
    index_file = static_dir / "index.html"
    if index_file.is_file():
        return FileResponse(index_file)
    return {"message": "Bienvenue sur PriceWatch API. Rendez-vous sur /docs pour tester l'API Swagger."}


@app.get("/health", tags=["Système"], summary="Vérification de l'état de l'application")
def health_check():
    """Indique si l'application et l'API fonctionnent correctement."""
    return {"status": "ok", "app": "PriceWatch", "version": "1.0.0"}
