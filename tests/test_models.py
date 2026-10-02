from app.models import Product, Store, ProductSource, PriceHistory, Alert


def test_create_product_and_store(db_session):
    """Vérifie la création d'un produit et d'un magasin avec relation."""
    store = Store(name="TestShop", url="https://testshop.com")
    product = Product(name="Casque Audio Test")
    db_session.add_all([store, product])
    db_session.commit()

    assert product.id is not None
    assert store.id is not None
    assert product.name == "Casque Audio Test"
    assert store.name == "TestShop"


def test_create_product_source_and_history(db_session):
    """Vérifie l'enregistrement d'une source et de l'historique des prix."""
    store = Store(name="ShopA", url="demo_sites/shop_a.html")
    product = Product(name="Sony WH-1000XM5")
    db_session.add_all([store, product])
    db_session.commit()

    source = ProductSource(
        product_id=product.id,
        store_id=store.id,
        url="demo_sites/shop_a.html",
        alert_threshold=280.0
    )
    db_session.add(source)
    db_session.commit()

    history = PriceHistory(
        product_source_id=source.id,
        price=275.0
    )
    db_session.add(history)
    db_session.commit()

    assert source.id is not None
    assert history.id is not None
    assert history.price == 275.0
    assert history.source.product.name == "Sony WH-1000XM5"


def test_create_alert_when_threshold_reached(db_session):
    """Vérifie l'enregistrement d'une alerte en base de données."""
    store = Store(name="ShopB", url="demo_sites/shop_b.html")
    product = Product(name="Sony WH-1000XM5")
    db_session.add_all([store, product])
    db_session.commit()

    source = ProductSource(
        product_id=product.id,
        store_id=store.id,
        url="demo_sites/shop_b.html",
        alert_threshold=280.0
    )
    db_session.add(source)
    db_session.commit()

    # Le prix baisse à 270 € (seuil à 280 €) -> création d'alerte
    alert = Alert(
        product_source_id=source.id,
        price=270.0,
        message="Baisse de prix détectée !",
        is_read=False
    )
    db_session.add(alert)
    db_session.commit()

    assert alert.id is not None
    assert alert.price == 270.0
    assert alert.is_read is False
