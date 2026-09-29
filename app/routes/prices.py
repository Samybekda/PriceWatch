from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, ProductSource, Store, PriceHistory, Alert
from app.schemas import ScrapeReport, StoreRead, StoreCreate
try:
    from app.services.scraper_service import scrape_all_sources
except ImportError:
    def scrape_all_sources(db: Session):
        return {
            "total_sources": 0,
            "prices_recorded": 0,
            "alerts_created": 0,
            "details": ["Module de scraping en cours d'intégration (Jour 3)."]
        }


router = APIRouter(tags=["Prix & Scraping"])


@router.get("/products/{product_id}/prices", summary="Historique des prix d'un produit")
def get_product_prices(product_id: int, db: Session = Depends(get_db)):
    """
    Retourne l'historique complet des prix pour un produit donné,
    groupé par magasin, idéal pour alimenter un graphique d'évolution dans le frontend.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    result = {
        "product_id": product.id,
        "product_name": product.name,
        "stores": []
    }

    for source in product.sources:
        store_name = source.store.name if source.store else "Inconnu"
        history_records = (
            db.query(PriceHistory)
            .filter(PriceHistory.product_source_id == source.id)
            .order_by(PriceHistory.collected_at.asc())
            .all()
        )

        points = [
            {
                "id": h.id,
                "price": h.price,
                "collected_at": h.collected_at.isoformat()
            }
            for h in history_records
        ]

        result["stores"].append({
            "source_id": source.id,
            "store_name": store_name,
            "url": source.url,
            "alert_threshold": source.alert_threshold,
            "current_price": points[-1]["price"] if points else None,
            "history": points
        })

    return result


@router.post("/scrape", response_model=ScrapeReport, summary="Lancer la collecte des prix (Scraping)")
def trigger_scrape(db: Session = Depends(get_db)):
    """
    Déclenche manuellement la récupération des prix pour l'ensemble des sources enregistrées.
    Enregistre les nouveaux prix et déclenche des alertes si les seuils sont atteints.
    """
    report = scrape_all_sources(db)
    return report


@router.get("/stats", summary="Statistiques globales pour le tableau de bord")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Fournit les statistiques clés pour le tableau de bord :
    - Nombre de produits surveillés
    - Nombre de sites marchands
    - Nombre total de relevés de prix
    - Dernières alertes générées
    """
    products_count = db.query(Product).count()
    stores_count = db.query(Store).count()
    sources_count = db.query(ProductSource).count()
    prices_count = db.query(PriceHistory).count()
    unread_alerts_count = db.query(Alert).filter(Alert.is_read == False).count()

    # Dernières alertes
    latest_alerts = (
        db.query(Alert)
        .order_by(Alert.created_at.desc())
        .limit(5)
        .all()
    )

    alerts_data = []
    for a in latest_alerts:
        prod_name = a.source.product.name if a.source and a.source.product else "Produit"
        store_name = a.source.store.name if a.source and a.source.store else "Magasin"
        alerts_data.append({
            "id": a.id,
            "product_name": prod_name,
            "store_name": store_name,
            "price": a.price,
            "message": a.message,
            "created_at": a.created_at.isoformat(),
            "is_read": a.is_read
        })

    return {
        "products_count": products_count,
        "stores_count": stores_count,
        "sources_count": sources_count,
        "prices_count": prices_count,
        "unread_alerts_count": unread_alerts_count,
        "latest_alerts": alerts_data
    }


@router.get("/stores", response_model=List[StoreRead], summary="Lister les magasins e-commerce")
def list_stores(db: Session = Depends(get_db)):
    """Retourne la liste des magasins disponibles."""
    return db.query(Store).order_by(Store.name.asc()).all()


@router.post("/stores", response_model=StoreRead, summary="Créer un magasin")
def create_store(payload: StoreCreate, db: Session = Depends(get_db)):
    """Ajoute un nouveau magasin."""
    existing = db.query(Store).filter(Store.name == payload.name.strip()).first()
    if existing:
        return existing
    store = Store(name=payload.name.strip(), url=payload.url)
    db.add(store)
    db.commit()
    db.refresh(store)
    return store
