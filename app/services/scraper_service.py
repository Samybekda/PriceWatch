import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models import ProductSource, PriceHistory, Alert
from scrapers import get_scraper

logger = logging.getLogger("pricewatch.scraper")


def scrape_source(db: Session, source: ProductSource) -> Dict[str, Any]:
    """
    Exécute le scraping pour une source produit spécifique (un produit sur un magasin donné).
    Enregistre le prix dans l'historique et déclenche une alerte si le prix est inférieur ou égal au seuil.
    """
    store_name = source.store.name if source.store else "Inconnu"
    product_name = source.product.name if source.product else "Produit"

    scraper = get_scraper(store_name=store_name, url=source.url)
    price = scraper.get_price(source.url, product_name=product_name)

    if price is None:
        return {
            "source_id": source.id,
            "product": product_name,
            "store": store_name,
            "success": False,
            "message": f"Impossible d'extraire le prix pour {product_name} sur {store_name} ({source.url})"
        }

    # 1. Enregistrement dans l'historique des prix
    history_entry = PriceHistory(
        product_source_id=source.id,
        price=price
    )
    db.add(history_entry)

    # 2. Vérification du seuil d'alerte
    alert_triggered = False
    alert_msg = ""
    if source.alert_threshold is not None and price <= source.alert_threshold:
        alert_msg = f"🔔 Le prix du {product_name} est passé à {price:g} € sur {store_name} (seuil : {source.alert_threshold:g} €)."
        
        # Création de l'alerte en base de données
        new_alert = Alert(
            product_source_id=source.id,
            price=price,
            message=alert_msg,
            is_read=False
        )
        db.add(new_alert)
        alert_triggered = True

    db.commit()

    return {
        "source_id": source.id,
        "product": product_name,
        "store": store_name,
        "price": price,
        "success": True,
        "alert_triggered": alert_triggered,
        "message": alert_msg if alert_triggered else f"Prix relevé : {price:g} €"
    }


def scrape_all_sources(db: Session) -> Dict[str, Any]:
    """
    Parcourt toutes les sources enregistrées dans la base de données
    et met à jour leurs prix.
    """
    sources = db.query(ProductSource).all()
    total = len(sources)
    prices_recorded = 0
    alerts_created = 0
    details: List[str] = []

    for source in sources:
        try:
            res = scrape_source(db, source)
            if res.get("success"):
                prices_recorded += 1
                details.append(f"[{res['store']}] {res['product']} : {res['price']} €")
                if res.get("alert_triggered"):
                    alerts_created += 1
            else:
                details.append(f"[ERREUR] {res['message']}")
        except Exception as e:
            logger.error(f"Erreur scraping source {source.id}: {e}")
            details.append(f"[ERREUR] Source {source.id} : {str(e)}")

    return {
        "total_sources": total,
        "prices_recorded": prices_recorded,
        "alerts_created": alerts_created,
        "details": details
    }
