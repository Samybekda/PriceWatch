import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Chemin du dossier racine de PriceWatch
BASE_DIR = Path(__file__).resolve().parent.parent

# URL de la base de données :
# Par défaut SQLite pour la simplicité (stocké dans pricewatch/pricewatch.db).
# Peut être remplacé par PostgreSQL via la variable d'environnement DATABASE_URL.
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'pricewatch.db'}")

# Création du moteur SQLAlchemy
# Pour SQLite, "check_same_thread": False est requis par FastAPI car plusieurs threads traitent les requêtes.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Fabrique de sessions pour communiquer avec la base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour déclarer nos modèles ORM
Base = declarative_base()


def get_db():
    """
    Générateur de dépendance pour FastAPI.
    Fournit une session de base de données par requête HTTP,
    puis la referme automatiquement une fois la requête terminée.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
