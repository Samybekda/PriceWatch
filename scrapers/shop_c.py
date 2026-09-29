from bs4 import BeautifulSoup
from .base import BaseScraper


class ShopCScraper(BaseScraper):
    """
    Scraper pour le magasin ShopC (HighTech Express).
    Structure HTML attendue :
    <div class="item-card">
        <div class="title">Sony WH-1000XM5</div>
        <span class="amount" id="current-price">289.00 €</span>
    </div>
    """

    name = "ShopC"

    def extract_price(self, soup: BeautifulSoup, product_name: str = None) -> float | None:
        cards = soup.find_all("div", class_="item-card")

        # Si un nom de produit est spécifié
        if product_name and cards:
            for card in cards:
                title_elem = card.find(class_="title")
                if title_elem and product_name.lower() in title_elem.text.lower():
                    price_elem = card.find(class_="amount")
                    if price_elem:
                        return self.clean_price(price_elem.text)

        # Sinon, cherche par ID ou classe
        price_elem = soup.find(id="current-price") or soup.find(class_="amount")
        if price_elem:
            return self.clean_price(price_elem.text)

        return None
