from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


# ==========================================
# Schémas pour les Magasins (Store)
# ==========================================
class StoreBase(BaseModel):
    name: str
    url: Optional[str] = None


class StoreCreate(StoreBase):
    pass


class StoreRead(StoreBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Schémas pour l'Historique de Prix (PriceHistory)
# ==========================================
class PriceHistoryRead(BaseModel):
    id: int
    product_source_id: int
    price: float
    collected_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Schémas pour les Sources Marchandes (ProductSource)
# ==========================================
class ProductSourceCreate(BaseModel):
    store_id: int
    url: str
    alert_threshold: Optional[float] = None


class ProductSourceRead(BaseModel):
    id: int
    product_id: int
    store_id: int
    store_name: Optional[str] = None
    url: str
    alert_threshold: Optional[float] = None
    current_price: Optional[float] = None
    last_updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Schémas pour les Produits (Product)
# ==========================================
class ProductCreate(BaseModel):
    name: str
    # Optionnel lors de la création d'un produit : ajouter directement une première source
    store_name: Optional[str] = None
    url: Optional[str] = None
    alert_threshold: Optional[float] = None


class ProductRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    sources: List[ProductSourceRead] = []
    best_price: Optional[float] = None
    best_store: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Schémas pour les Alertes (Alert)
# ==========================================
class AlertRead(BaseModel):
    id: int
    product_source_id: int
    product_name: Optional[str] = None
    store_name: Optional[str] = None
    price: float
    message: str
    created_at: datetime
    is_read: bool

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Schéma pour le rapport de Scraping
# ==========================================
class ScrapeReport(BaseModel):
    total_sources: int
    prices_recorded: int
    alerts_created: int
    details: List[str] = []
