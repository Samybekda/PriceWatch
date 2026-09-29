import re
from pathlib import Path
from bs4 import BeautifulSoup
import requests


class BaseScraper:
    """
    Classe de base pour tous les scrapers de PriceWatch.
    Chaque site marchand hérite de cette classe et implémente sa propre méthode 'extract_price'.
    """

    name = "Base"

    def fetch_html(self, url: str) -> str:
        """
        Récupère le contenu HTML d'une page :
        - Soit depuis une URL web (http:// ou https://) avec la bibliothèque requests.
        - Soit depuis un fichier local (pratique pour les démonstrations et les tests).
        """
        # Si c'est une URL web standard
        if url.startswith("http://") or url.startswith("https://"):
            headers = {
                "User-Agent": "PriceWatch-Bot/1.0 (Projet Etudiant L3 MIAGE Toulouse; contact@univ-tlse3.fr)"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text

        # Si c'est un chemin de fichier local (ex: demo_sites/shop_a.html ou file://...)
        clean_path = url.replace("file:///", "").replace("file://", "")
        file_path = Path(clean_path)

        # Si chemin relatif, on tente de le résoudre depuis la racine du projet
        if not file_path.is_file():
            base_dir = Path(__file__).resolve().parent.parent
            file_path = base_dir / clean_path

        if not file_path.is_file():
            raise FileNotFoundError(f"Page locale introuvable : {url}")

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def clean_price(price_text: str) -> float | None:
        """
        Nettoie une chaîne de caractères représentant un prix (ex: ' 279,00 € ')
        et la convertit en float (ex: 279.0).
        """
        if not price_text:
            return None

        # Remplacement de la virgule par un point
        text = price_text.replace(",", ".")
        # Extraction du motif numérique (ex: 299 ou 299.99)
        match = re.search(r"(\d+(?:\.\d+)?)", text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None

    def extract_price(self, soup: BeautifulSoup, product_name: str = None) -> float | None:
        """
        Méthode à surcharger dans les sous-classes pour extraire le prix
        selon la structure HTML spécifique du magasin.
        """
        raise NotImplementedError("Chaque scraper doit implémenter extract_price()")

    def get_price(self, url: str, product_name: str = None) -> float | None:
        """
        Méthode principale : récupère le HTML, analyse avec BeautifulSoup et retourne le prix.
        """
        html = self.fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")
        return self.extract_price(soup, product_name=product_name)
