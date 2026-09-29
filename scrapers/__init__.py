from typing import Optional
from bs4 import BeautifulSoup
from .base import BaseScraper
from .shop_a import ShopAScraper
from .shop_b import ShopBScraper
from .shop_c import ShopCScraper


class GenericScraper(BaseScraper):
    """
    Scraper générique de secours pour les sites sans scraper dédié.
    Cherche les balises couramment utilisées pour afficher les prix.
    """
    name = "Generic"

    def extract_price(self, soup: BeautifulSoup, product_name: str = None) -> float | None:
        # Si un nom de produit est fourni, chercher d'abord le bloc parent qui contient ce nom
        if product_name:
            for card in soup.find_all(["div", "article", "section", "li"]):
                if product_name.lower() in card.text.lower():
                    price_tag = card.find(class_=["price", "price-value", "amount", "prix", "product-price"])
                    if price_tag:
                        price = self.clean_price(price_tag.text)
                        if price:
                            return price

        # Essai 1 : attributs de micro-données e-commerce schema.org
        price_tag = soup.find(attrs={"itemprop": "price"})
        if price_tag:
            content = price_tag.get("content") or price_tag.text
            price = self.clean_price(content)
            if price:
                return price

        # Essai 2 : classes CSS courantes
        common_selectors = [".price", ".prix", ".product-price", ".current-price", ".offer-price", ".amount"]
        for sel in common_selectors:
            elem = soup.select_one(sel)
            if elem:
                price = self.clean_price(elem.text)
                if price:
                    return price

        return None


# Dictionnaire de registre reliant le nom du magasin à son scraper
SCRAPER_REGISTRY = {
    "ShopA": ShopAScraper(),
    "ShopB": ShopBScraper(),
    "ShopC": ShopCScraper(),
}

DEFAULT_SCRAPER = GenericScraper()


def get_scraper(store_name: Optional[str] = None, url: Optional[str] = None) -> BaseScraper:
    """
    Retourne le scraper adapté en fonction du nom du magasin ou de l'URL.
    """
    if store_name and store_name in SCRAPER_REGISTRY:
        return SCRAPER_REGISTRY[store_name]

    if url:
        url_lower = url.lower()
        if "shop_a" in url_lower or "shopa" in url_lower:
            return SCRAPER_REGISTRY["ShopA"]
        if "shop_b" in url_lower or "shopb" in url_lower:
            return SCRAPER_REGISTRY["ShopB"]
        if "shop_c" in url_lower or "shopc" in url_lower:
            return SCRAPER_REGISTRY["ShopC"]

    return DEFAULT_SCRAPER
