"""
Script d'automatisation du scraping PriceWatch.

Usage :
    python scraper.py

Fonctionnement :
    1. Se connecte à la base de données SQLite.
    2. Récupère l'ensemble des sources de produits configurées.
    3. Exécute les scrapers correspondants pour relever les nouveaux prix.
    4. Enregistre chaque relevé dans la table 'price_history'.
    5. Déclenche et enregistre une alerte si le prix <= seuil configuré.

Automatisation avec cron sous Linux :
    Pour exécuter ce script automatiquement toutes les heures, ajoutez
    la ligne suivante dans votre crontab (`crontab -e`) :
    0 * * * * /chemin/vers/venv/bin/python /chemin/vers/pricewatch/scraper.py >> /var/log/pricewatch.log 2>&1
"""

import sys
from datetime import datetime
from app.database import SessionLocal
from app.services.scraper_service import scrape_all_sources


def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Lancement du scraping des prix...")
    
    db = SessionLocal()
    try:
        report = scrape_all_sources(db)
        print("--------------------------------------------------")
        print(f"Total sources traitees   : {report['total_sources']}")
        print(f"Prix enregistres         : {report['prices_recorded']}")
        print(f"Nouvelles alertes creees : {report['alerts_created']}")
        print("--------------------------------------------------")
        print("Details des operations :")
        for detail in report["details"]:
            print(f" - {detail}")
        print("--------------------------------------------------")
        print("[OK] Session de scraping terminee avec succes.")
        return 0
    except Exception as e:
        print(f"[ERREUR] Echec lors du scraping : {e}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
