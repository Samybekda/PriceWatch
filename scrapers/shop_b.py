from bs4 import BeautifulSoup
from .base import BaseScraper


class ShopBScraper(BaseScraper):
    """
    Scraper pour le magasin ShopB (Tech Mania).
    Structure HTML attendue :
    <div class="product-box">
        <h2 class="item-name">Sony WH-1000XM5</h2>
        <span class="price-value">279,00</span>
    </div>
    """

    name = "ShopB"

    def extract_price(self, soup: BeautifulSoup, product_name: str = None) -> float | None:
        boxes = soup.find_all("div", class_="product-box")

        # Si un nom de produit est spécifié, on cible la boîte correspondante
        if product_name and boxes:
            for box in boxes:
                title_elem = box.find(class_="item-name")
                if title_elem and product_name.lower() in title_elem.text.lower():
                    price_elem = box.find(class_="price-value")
                    if price_elem:
                        return self.clean_price(price_elem.text)

        # Sinon, on cherche la première classe .price-value
        price_elem = soup.find(class_="price-value")
        if price_elem:
            return self.clean_price(price_elem.text)

        return None
