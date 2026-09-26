from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


def utc_now():
    """Retourne la date et l'heure actuelles en UTC."""
    return datetime.now(timezone.utc)


class Product(Base):
    """
    Table 'products' : Représente un produit générique suivi par l'utilisateur.
    Exemple : 'Sony WH-1000XM5', 'iPhone 15 128Go'.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    created_at = Column(DateTime, default=utc_now)

    # Relations : un produit peut avoir plusieurs sources marchandes (ShopA, ShopB...)
    sources = relationship("ProductSource", back_populates="product", cascade="all, delete-orphan")


class Store(Base):
    """
    Table 'stores' : Représente un magasin / site e-commerce.
    Exemple : 'ShopA', 'ShopB', 'ShopC'.
    """
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    url = Column(String(255), nullable=True)

    # Relations
    sources = relationship("ProductSource", back_populates="store", cascade="all, delete-orphan")


class ProductSource(Base):
    """
    Table 'product_sources' : Fait le lien entre un produit et un magasin spécifique.
    Contient l'URL de la fiche produit sur ce magasin et le seuil d'alerte configuré.
    """
    __tablename__ = "product_sources"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(500), nullable=False)
    alert_threshold = Column(Float, nullable=True)

    # Relations
    product = relationship("Product", back_populates="sources")
    store = relationship("Store", back_populates="sources")
    price_history = relationship("PriceHistory", back_populates="source", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="source", cascade="all, delete-orphan")


class PriceHistory(Base):
    """
    Table 'price_history' : Historique des relevés de prix.
    À chaque passage du scraper, un enregistrement est créé ici.
    """
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_source_id = Column(Integer, ForeignKey("product_sources.id", ondelete="CASCADE"), nullable=False)
    price = Column(Float, nullable=False)
    collected_at = Column(DateTime, default=utc_now)

    # Relation
    source = relationship("ProductSource", back_populates="price_history")


class Alert(Base):
    """
    Table 'alerts' : Alertes créées lorsque le prix actuel descend sous le seuil d'alerte.
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    product_source_id = Column(Integer, ForeignKey("product_sources.id", ondelete="CASCADE"), nullable=False)
    price = Column(Float, nullable=False)
    message = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=utc_now)
    is_read = Column(Boolean, default=False)

    # Relation
    source = relationship("ProductSource", back_populates="alerts")
