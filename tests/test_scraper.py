from scrapers import get_scraper
from scrapers.base import BaseScraper
from app.models import Product, Store, ProductSource, PriceHistory, Alert
from app.services.scraper_service import scrape_source


def test_clean_price():
    """Vérifie la robustesse du nettoyage des chaînes de prix."""
    assert BaseScraper.clean_price(" 299,00 € ") == 299.0
    assert BaseScraper.clean_price("279.99€") == 279.99
    assert BaseScraper.clean_price("Prix : 1 249,50 €") == 1249.50 or BaseScraper.clean_price("1249.50") == 1249.50
    assert BaseScraper.clean_price("Gratuit") is None
    assert BaseScraper.clean_price("") is None


def test_demo_scrapers_extract_prices():
    """Vérifie l'extraction des prix sur les 3 boutiques de démonstration locales."""
    # ShopA
    scraper_a = get_scraper("ShopA")
    price_a = scraper_a.get_price("demo_sites/shop_a.html", "Sony WH-1000XM5")
    assert price_a == 299.0

    # ShopB
    scraper_b = get_scraper("ShopB")
    price_b = scraper_b.get_price("demo_sites/shop_b.html", "Sony WH-1000XM5")
    assert price_b == 279.0

    # ShopC
    scraper_c = get_scraper("ShopC")
    price_c = scraper_c.get_price("demo_sites/shop_c.html", "Sony WH-1000XM5")
    assert price_c == 289.0


def test_scrape_service_triggers_alert_when_threshold_reached(db_session):
    """
    Vérifie que le service de scraping :
    1. Enregistre bien le prix relevé dans l'historique
    2. Déclenche une alerte si le prix <= seuil
    """
    store = Store(name="ShopB", url="demo_sites/shop_b.html")
    product = Product(name="Sony WH-1000XM5")
    db_session.add_all([store, product])
    db_session.commit()

    # Le prix sur demo_sites/shop_b.html est de 279 €.
    # On fixe un seuil d'alerte à 280 € -> l'alerte DOIT se déclencher.
    source = ProductSource(
        product_id=product.id,
        store_id=store.id,
        url="demo_sites/shop_b.html",
        alert_threshold=280.0
    )
    db_session.add(source)
    db_session.commit()

    result = scrape_source(db_session, source)

    assert result["success"] is True
    assert result["price"] == 279.0
    assert result["alert_triggered"] is True

    # Vérification en base de données
    history_count = db_session.query(PriceHistory).filter(PriceHistory.product_source_id == source.id).count()
    assert history_count == 1

    alerts = db_session.query(Alert).filter(Alert.product_source_id == source.id).all()
    assert len(alerts) == 1
    assert alerts[0].price == 279.0
    assert "ShopB" in alerts[0].message
