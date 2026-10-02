"""
Script d'initialisation (seeding) de la base de données PriceWatch.
Permet à un étudiant ou un examinateur de démarrer directement
avec des données réalistes prêtes à être testées et présentées.
"""

from datetime import datetime, timedelta, timezone
from app.database import engine, Base, SessionLocal
from app.models import Product, Store, ProductSource, PriceHistory, Alert


def seed_database():
    print("Initialisation des tables de la base de données...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Si des produits existent déjà, on ne réinsère pas
        if db.query(Product).count() > 0:
            print("La base de données contient déjà des données. Aucun ajout nécessaire.")
            return

        print("Insertion des magasins de démonstration...")
        shop_a = Store(name="ShopA", url="demo_sites/shop_a.html")
        shop_b = Store(name="ShopB", url="demo_sites/shop_b.html")
        shop_c = Store(name="ShopC", url="demo_sites/shop_c.html")
        db.add_all([shop_a, shop_b, shop_c])
        db.commit()

        print("Insertion des produits surveillés...")
        sony = Product(name="Sony WH-1000XM5")
        iphone = Product(name="iPhone 15 128Go")
        db.add_all([sony, iphone])
        db.commit()

        print("Association des sources marchandes aux produits...")
        # Sony WH-1000XM5 sur les 3 boutiques
        src_sony_a = ProductSource(
            product_id=sony.id,
            store_id=shop_a.id,
            url="demo_sites/shop_a.html",
            alert_threshold=280.0
        )
        src_sony_b = ProductSource(
            product_id=sony.id,
            store_id=shop_b.id,
            url="demo_sites/shop_b.html",
            alert_threshold=280.0  # Le prix sur ShopB sera 279€ -> déclenchera l'alerte !
        )
        src_sony_c = ProductSource(
            product_id=sony.id,
            store_id=shop_c.id,
            url="demo_sites/shop_c.html",
            alert_threshold=280.0
        )

        # iPhone 15 sur ShopA et ShopB
        src_iphone_a = ProductSource(
            product_id=iphone.id,
            store_id=shop_a.id,
            url="demo_sites/shop_a.html",
            alert_threshold=830.0
        )
        src_iphone_b = ProductSource(
            product_id=iphone.id,
            store_id=shop_b.id,
            url="demo_sites/shop_b.html",
            alert_threshold=830.0  # Prix 829€ -> déclenchera l'alerte !
        )

        db.add_all([src_sony_a, src_sony_b, src_sony_c, src_iphone_a, src_iphone_b])
        db.commit()

        print("Génération de l'historique des prix pour les graphiques...")
        now = datetime.now(timezone.utc)

        # Historique Sony
        history_points = [
            # Il y a 3 jours
            PriceHistory(product_source_id=src_sony_a.id, price=319.0, collected_at=now - timedelta(days=3)),
            PriceHistory(product_source_id=src_sony_b.id, price=309.0, collected_at=now - timedelta(days=3)),
            PriceHistory(product_source_id=src_sony_c.id, price=315.0, collected_at=now - timedelta(days=3)),
            # Il y a 2 jours
            PriceHistory(product_source_id=src_sony_a.id, price=309.0, collected_at=now - timedelta(days=2)),
            PriceHistory(product_source_id=src_sony_b.id, price=289.0, collected_at=now - timedelta(days=2)),
            PriceHistory(product_source_id=src_sony_c.id, price=299.0, collected_at=now - timedelta(days=2)),
            # Il y a 1 jour
            PriceHistory(product_source_id=src_sony_a.id, price=299.0, collected_at=now - timedelta(days=1)),
            PriceHistory(product_source_id=src_sony_b.id, price=279.0, collected_at=now - timedelta(days=1)),
            PriceHistory(product_source_id=src_sony_c.id, price=289.0, collected_at=now - timedelta(days=1)),
        ]
        db.add_all(history_points)

        print("Création d'une alerte de démonstration...")
        demo_alert = Alert(
            product_source_id=src_sony_b.id,
            price=279.0,
            message="🔔 Le prix du Sony WH-1000XM5 est passé à 279 € sur ShopB.",
            created_at=now - timedelta(hours=4),
            is_read=False
        )
        db.add(demo_alert)

        db.commit()
        print("[OK] Base de donnees initialisee avec succes avec des donnees de test !")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
