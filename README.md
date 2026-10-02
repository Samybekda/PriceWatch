# 🏷️ PriceWatch - Comparateur & Surveillance de Prix Multi-sites

> **Projet académique L3 MIAGE - Université de Toulouse**  
> Développé par un étudiant en Licence 3 Méthodes Informatiques Appliquées à la Gestion des Entreprises (MIAGE).

---

## 1. Présentation du projet

**PriceWatch** est une application web et une API permettant de surveiller automatiquement les prix d'articles sur différents sites de commerce en ligne, de comparer les offres en mettant en valeur le meilleur prix, de tracer l'historique d'évolution dans un graphique et de déclencher des alertes immédiates dès qu'un prix descend sous un seuil choisi par l'utilisateur.

Le projet a été conçu selon des principes de **sobriété logicielle**, de **lisibilité du code** et de **séparation claire des responsabilités**, permettant une compréhension intégrale de chaque composant technique et une présentation fluide lors d'un entretien de stage.

---

## 2. Objectifs

* **Maîtriser une pile logicielle moderne et légère :** Développer une application complète de bout en bout (Frontend &rarr; API REST FastAPI &rarr; Base de données relationnelle SQLite/PostgreSQL).
* **Collecter et traiter la donnée web :** Mettre en œuvre un système de scraping éthique, propre et modulaire avec `requests` et `BeautifulSoup`.
* **Automatiser les traitements :** Mettre en place un script indépendant planifiable via les tâches planifiées Linux (`cron`).
* **Concevoir un modèle relationnel cohérent :** Structurer les relations 1-N (produits, magasins, sources, historiques, alertes) avec SQLAlchemy.
* **Assurer la qualité logicielle :** Valider les opérations critiques (CRUD, détection de baisse, alertes) avec une suite de tests unitaires et d'intégration `pytest`.

---

## 3. Fonctionnalités

1. **Gestion des produits & sources :**
   * Enregistrement de produits génériques (ex: *Sony WH-1000XM5*, *iPhone 15*).
   * Association de multiples magasins et fiches produits à un même article.
   * Définition d'un seuil d'alerte en euros.
2. **Comparateur de prix multi-sites :**
   * Tableau comparatif en temps réel des offres.
   * Mise en évidence automatique du **prix le moins cher** (badge vert *🏆 Meilleur prix*).
3. **Historique & Visualisation graphique :**
   * Enregistrement horodaté de chaque relevé de prix.
   * Graphique interactif multi-courbes avec [Chart.js](https://www.chartjs.org/) permettant de visualiser les tendances de chaque boutique.
4. **Système d'alertes automatiques :**
   * Détection de la condition : `prix_actuel <= seuil_alerte`.
   * Enregistrement de l'alerte en base de données et notification visuelle dans l'interface (avec possibilité de marquer comme lue ou de supprimer).
5. **Pages de démonstration locales (Sandbox) :**
   * Fourniture de 3 sites marchands fictifs (`ShopA`, `ShopB`, `ShopC`) permettant d'exécuter et tester le scraping en local sans dépendance réseau externe ni risque de blocage.

---

## 4. Technologies utilisées

* **Langage :** Python 3.12+ (lisibilité, typage statique optionnel avec `typing`).
* **Framework Backend / API :** [FastAPI](https://fastapi.tiangolo.com/) (haute performance, documentation Swagger automatique, validation par [Pydantic](https://docs.pydantic.dev/)).
* **Base de données & ORM :** [SQLAlchemy](https://www.sqlalchemy.org/) 2.0 avec **SQLite** (développement local) et compatibilité native **PostgreSQL**.
* **Scraping Web :** `requests` (requêtes HTTP) et `BeautifulSoup4` (analyse du DOM HTML).
* **Interface Utilisateur :** HTML5 sémantique, CSS3 moderne (variables CSS, design responsive) et JavaScript Vanilla (Fetch API, manipulation du DOM sans framework lourd).
* **Visualisation :** [Chart.js](https://www.chartjs.org/) (rendu des courbes d'évolution des prix).
* **Tests automatisés :** [Pytest](https://docs.pytest.org/) avec client de test `httpx`.
* **Automatisation :** CLI Python et `cron` (Linux).
* **Conteneurisation :** Docker (déploiement reproductible).

---

## 5. Architecture de l'application

Le projet applique une architecture 3-tiers découplée :

```text
       Navigateur Web (Client)
      [HTML / CSS / JavaScript]
                 │
                 │ Requêtes HTTP (Fetch JSON)
                 ▼
          API REST FastAPI
    ┌───────────────────────────┐
    │  - routes/products.py     │
    │  - routes/prices.py       │
    │  - routes/alerts.py       │
    │  - services/scraper.py    │
    └─────────────┬─────────────┘
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
Scrapers Web           Base de Données
(ShopA, ShopB, ShopC)   (SQLite / PostgreSQL)
```

### Organisation des dossiers

```text
pricewatch/
│
├── app/
│   ├── main.py                  # Point d'entrée de l'application FastAPI
│   ├── database.py              # Configuration de SQLAlchemy et session DB
│   ├── models.py                # Modèles de données ORM (tables SQL)
│   ├── schemas.py               # Schémas Pydantic (validation & sérialisation)
│   ├── routes/                  # Endpoints de l'API
│   │   ├── products.py          # CRUD Produits et sources
│   │   ├── prices.py            # Historique de prix, statistiques & scraping
│   │   └── alerts.py            # Consultation et gestion des alertes
│   ├── services/
│   │   └── scraper_service.py   # Logique métier de scraping et alertes
│   └── static/                  # Interface web (Frontend)
│       ├── index.html           # Page principale (Dashboard, Produits, Graphiques)
│       ├── css/style.css        # Styles de l'interface
│       └── js/app.js            # Logique frontend asynchrone
│
├── scrapers/                    # Modules de scraping modulaires
│   ├── base.py                  # Classe abstraite BaseScraper (fetch & nettoyage)
│   ├── shop_a.py                # Scraper dédié à ShopA
│   ├── shop_b.py                # Scraper dédié à ShopB
│   ├── shop_c.py                # Scraper dédié à ShopC
│   └── __init__.py              # Registre et sélecteur de scraper
│
├── demo_sites/                  # Pages marchandes locales de démonstration
│   ├── shop_a.html              # Électro Discount
│   ├── shop_b.html              # Tech Mania
│   └── shop_c.html              # HighTech Express
│
├── tests/                       # Suite de tests Pytest
│   ├── conftest.py              # Configuration SQLite in-memory & client FastAPI
│   ├── test_models.py           # Tests des modèles relationnels
│   ├── test_api.py              # Tests des routes de l'API REST
│   └── test_scraper.py          # Tests des scrapers et déclenchement d'alertes
│
├── scraper.py                   # Script exécutable en CLI ou via cron Linux
├── seed.py                      # Initialisation de la base avec données de test
├── run.py                       # Démarrage rapide du serveur de développement
├── requirements.txt             # Dépendances Python
├── Dockerfile                   # Fichier Docker pour conteneurisation
└── README.md                    # Documentation complète
```

---

## 6. Installation

### Prérequis
* Python 3.10 ou supérieur installé.
* Git.

### Étapes d'installation

1. **Cloner ou ouvrir le dossier du projet :**
   ```bash
   cd pricewatch
   ```

2. **Créer un environnement virtuel Python :**
   ```bash
   # Sous Linux / macOS :
   python3 -m venv .venv
   source .venv/bin/activate

   # Sous Windows (PowerShell) :
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Installer les dépendances requises :**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialiser la base de données avec des données de test :**
   ```bash
   python seed.py
   ```
   *Ce script insère les boutiques démo, les produits (ex: Sony WH-1000XM5, iPhone 15), l'historique de prix et une première alerte.*

---

## 7. Lancement du projet

### Lancement standard (Développement)
Pour démarrer le serveur web FastAPI :
```bash
python run.py
```
*ou directement via uvicorn :*
```bash
uvicorn app.main:app --reload --port 8000
```

Accédez ensuite à votre navigateur :
* **Interface Web PriceWatch :** [http://localhost:8000/](http://localhost:8000/)
* **Documentation interactive Swagger :** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Documentation alternative ReDoc :** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Lancement avec Docker (Optionnel)
```bash
# Construction de l'image
docker build -t pricewatch .

# Démarrage du conteneur
docker run -p 8000:8000 pricewatch
```

---

## 8. Utilisation de l'application

1. **Tableau de bord (Dashboard) :**
   * Consultez les 4 indicateurs clés (produits suivis, boutiques, relevés de prix, alertes actives).
   * Consultez le résumé du comparateur et les dernières alertes.
2. **Ajouter un produit :**
   * Rendez-vous sur l'onglet **Produits & Comparateur**.
   * Remplissez le nom (ex: `Nintendo Switch OLED`), le magasin initial, l'URL (`demo_sites/shop_a.html`) et le seuil d'alerte (ex: `310 €`).
   * Cliquez sur **Enregistrer le produit**.
3. **Associer un autre magasin :**
   * Sur la fiche du produit, cliquez sur **+ Ajouter un magasin**.
   * Sélectionnez un deuxième magasin (`ShopB`), indiquez l'URL (`demo_sites/shop_b.html`) et le seuil.
4. **Lancer un relevé de prix :**
   * Cliquez sur le bouton bleu **🔄 Actualiser les prix** dans la barre supérieure.
   * L'API analyse les pages, relève les prix et actualise instantanément le tableau ainsi que les alertes.
5. **Visualiser l'évolution :**
   * Allez dans l'onglet **Historique & Graphique**.
   * Choisissez un produit dans la liste déroulante pour observer les courbes de prix par boutique.

---

## 9. Exemple de scraping

Le système de scraping est conçu de manière modulaire selon le patron de conception **Template Method / Strategy** :

1. **`BaseScraper` (`scrapers/base.py`) :**
   Prend en charge la récupération du HTML (que ce soit une URL HTTP distante ou un fichier HTML local) et fournit la méthode utilitaire `clean_price()` pour convertir des formats variés (`"279,00 €"`, `" 299.99 € "`) en nombre décimal `float`.
2. **Scrapers spécialisés (`shop_a.py`, `shop_b.py`, `shop_c.py`) :**
   Chaque boutique possède sa propre structure HTML. Par exemple pour `ShopB` :
   ```python
   class ShopBScraper(BaseScraper):
       name = "ShopB"
       def extract_price(self, soup: BeautifulSoup, product_name: str = None) -> float | None:
           # Recherche de la balise contenant le prix sur ShopB
           elem = soup.find(class_="price-value")
           return self.clean_price(elem.text) if elem else None
   ```
3. **Extensibilité :**
   Pour ajouter un nouveau magasin (ex: `ShopD`) :
   * Créer un fichier `scrapers/shop_d.py` héritant de `BaseScraper`.
   * Enregistrer la classe dans le dictionnaire `SCRAPER_REGISTRY` de `scrapers/__init__.py`.

---

## 10. Base de données relationnelle

La base est gérée via SQLAlchemy. Le modèle relationnel est le suivant :

```text
 ┌──────────────┐         1:N         ┌──────────────────┐
 │   products   │ ──────────────────< │ product_sources  │
 └──────────────┘                     └─────────┬────────┘
                                                │ N:1
 ┌──────────────┐         1:N                   │
 │    stores    │ ──────────────────────────────┘
 └──────────────┘                               │
                                                │ 1:N
                           ┌────────────────────┴────────────────────┐
                           │                                         │
                           ▼                                         ▼
                 ┌───────────────────┐                     ┌───────────────────┐
                 │   price_history   │                     │      alerts       │
                 └───────────────────┘                     └───────────────────┘
```

### Description des tables :
* **`products` :** `id` (PK), `name`, `created_at`.
* **`stores` :** `id` (PK), `name`, `url`.
* **`product_sources` :** `id` (PK), `product_id` (FK), `store_id` (FK), `url`, `alert_threshold`.
* **`price_history` :** `id` (PK), `product_source_id` (FK), `price`, `collected_at`.
* **`alerts` :** `id` (PK), `product_source_id` (FK), `price`, `message`, `created_at`, `is_read`.

> **💡 Passage à PostgreSQL :**  
> Pour basculer de SQLite à PostgreSQL en production, il suffit de définir la variable d'environnement :  
> `export DATABASE_URL="postgresql://user:password@localhost:5432/pricewatch"`  
> SQLAlchemy adapte automatiquement les requêtes sans modifier une seule ligne de code Python !

---

## 11. Automatisation avec cron sous Linux

Pour surveiller les prix sans intervention humaine, on utilise le script autonome `scraper.py` couplé au démon `cron` présent sur tous les systèmes Linux.

### Test manuel du script :
```bash
python scraper.py
```
Sortie attendue dans la console :
```text
[2026-09-28 20:55:46] Lancement du scraping des prix...
--------------------------------------------------
Total sources traitees   : 5
Prix enregistres         : 5
Nouvelles alertes creees : 2
--------------------------------------------------
Details des operations :
 - [ShopA] Sony WH-1000XM5 : 299.0 €
 - [ShopB] Sony WH-1000XM5 : 279.0 €
 - [ShopC] Sony WH-1000XM5 : 289.0 €
--------------------------------------------------
[OK] Session de scraping terminee avec succes.
```

### Configuration du cron :
1. Ouvrir la table des tâches cron de l'utilisateur :
   ```bash
   crontab -e
   ```
2. Ajouter l'une des planifications suivantes :

   * **Exécution toutes les heures :**
     ```cron
     0 * * * * /home/etudiant/pricewatch/.venv/bin/python /home/etudiant/pricewatch/scraper.py >> /home/etudiant/pricewatch/scraper.log 2>&1
     ```
   * **Exécution tous les jours à 8h00 :**
     ```cron
     0 8 * * * /home/etudiant/pricewatch/.venv/bin/python /home/etudiant/pricewatch/scraper.py >> /home/etudiant/pricewatch/scraper.log 2>&1
     ```

**Explication de la syntaxe cron :**
* `0 * * * *` : À la minute 0 de chaque heure, chaque jour.
* Le chemin absolu vers l'interpréteur Python du `.venv` assure que toutes les dépendances (`beautifulsoup4`, `requests`, etc.) sont bien chargées.
* `>> scraper.log 2>&1` : Redirige la sortie standard et les erreurs vers un fichier journal pour analyse ultérieure.

---

## 12. Tests automatisés

La qualité du code et la non-régression sont validées grâce à 11 tests automatisés avec **Pytest**.  
Une base de données SQLite en mémoire vive (`sqlite:///:memory:`) est automatiquement instanciée pour chaque test afin de garantir une isolation parfaite.

### Lancer la suite de tests :
```bash
pytest -v
```

### Détail des tests couverts :
* **Tests de modèles & relations (`test_models.py`) :**
  * Création d'un produit et d'un magasin.
  * Création d'une source marchande et insertion dans l'historique des prix.
  * Création et persistance d'une alerte lors du dépassement du seuil.
* **Tests de l'API REST (`test_api.py`) :**
  * `POST /api/products` & `GET /api/products/{id}`.
  * `GET /api/products` (listing).
  * `DELETE /api/products/{id}` (suppression et cascade).
  * `GET /api/products/{id}/prices` (historique formaté).
  * `GET /api/alerts` (consultation des alertes).
* **Tests de scraping (`test_scraper.py`) :**
  * Nettoyage des chaînes de prix (gestion des virgules, symboles €, espaces).
  * Extraction des prix sur les 3 boutiques démo (`ShopA`, `ShopB`, `ShopC`).
  * Scénario complet : relevé de prix et déclenchement automatique d'alerte lorsque `prix <= seuil`.

---

## 13. Compétences valorisées pour un stage (L3 MIAGE)

Ce projet illustre des compétences directement opérationnelles en entreprise :

1. **Python & Conception Orientée Objet :** Organisation en packages, utilisation de classes et d'héritage pour les scrapers, typage statique.
2. **Architecture Web & API REST :** Maîtrise de FastAPI, gestion des codes d'état HTTP (`200`, `201`, `404`), documentation interactive Swagger.
3. **Modélisation & Bases de données :** Modèle relationnel 1-N, clés primaires et étrangères, transactions SQL via SQLAlchemy ORM.
4. **Scraping de données :** Parsing de structures HTML avec BeautifulSoup, gestion des cas limites et extraction ciblée.
5. **Développement Frontend :** JavaScript asynchrone (`async/await`, `fetch`), manipulation dynamique du DOM, intégration de librairies graphiques (Chart.js).
6. **Automatisation Système :** Scripting CLI et ordonnancement via `cron` sous Linux.
7. **Bonnes pratiques d'ingénierie :** Tests unitaires (`pytest`), conteneurisation (`Docker`), contrôle de version (`Git`).

---

## 14. Améliorations possibles (Perspectives)

* Envoi de notifications par e-mail (via protocole SMTP) ou webhook Discord lors d'une alerte.
* Export des historiques de prix au format CSV ou Excel.
* Gestion de l'authentification des utilisateurs (JWT) pour permettre à chaque utilisateur d'avoir sa propre liste de produits surveillés.
* Détection automatique des promotions (pourcentage de réduction par rapport au prix moyen constaté).

---

## 15. Licence

Projet réalisé dans un cadre pédagogique - Université de Toulouse (L3 MIAGE). Libre d'utilisation à des fins d'apprentissage.
