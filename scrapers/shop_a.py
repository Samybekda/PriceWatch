from bs4 import BeautifulSoup
from .base import BaseScraper


class ShopAScraper(BaseScraper):
    """
    Scraper pour le magasin ShopA (Électro Discount).
    Structure HTML attendue :
    <div class="product-card">
        <div class="product-title">Sony WH-1000XM5</div>
        <span class="price">299.00 €</span>
    </div>
    """

    name = "ShopA"

    def extract_price(self, soup: BeautifulSoup, product_name: str = None) -> float | None:
        cards = soup.find_all("div", class_="product-card")
        
        # Si un nom de produit est spécifié, on cherche la carte correspondante
        if product_name and cards:
            for card in cards:
                title_elem = card.find("div", class_="product-title")
                if title_elem and product_name.lower() in title_elem.text.lower():
                    price_elem = card.find("span", class_="price")
                    if price_elem:
                        return self.clean_price(price_elem.text)

        # Sinon, on prend le premier élément .price trouvé sur la page
        price_elem = soup.find("span", class_="price")
        if price_elem:
            return self.clean_price(price_elem.text)

        return None
