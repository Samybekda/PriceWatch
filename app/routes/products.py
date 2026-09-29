from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, ProductSource, Store, PriceHistory
from app.schemas import ProductCreate, ProductRead, ProductSourceCreate, ProductSourceRead

router = APIRouter(tags=["Produits"])


def _build_product_read(product: Product, db: Session) -> dict:
    """Helper pour construire la vue détaillée d'un produit avec ses prix actuels."""
    sources_data = []
    best_price: Optional[float] = None
    best_store: Optional[str] = None

    for s in product.sources:
        # Récupère le dernier prix enregistré pour cette source
        latest_price_entry = (
            db.query(PriceHistory)
            .filter(PriceHistory.product_source_id == s.id)
            .order_by(PriceHistory.collected_at.desc())
            .first()
        )
        current_price = latest_price_entry.price if latest_price_entry else None
        last_updated = latest_price_entry.collected_at if latest_price_entry else None

        store_name = s.store.name if s.store else "Inconnu"

        sources_data.append({
            "id": s.id,
            "product_id": s.product_id,
            "store_id": s.store_id,
            "store_name": store_name,
            "url": s.url,
            "alert_threshold": s.alert_threshold,
            "current_price": current_price,
            "last_updated": last_updated
        })

        if current_price is not None:
            if best_price is None or current_price < best_price:
                best_price = current_price
                best_store = store_name

    return {
        "id": product.id,
        "name": product.name,
        "created_at": product.created_at,
        "sources": sources_data,
        "best_price": best_price,
        "best_store": best_store
    }


@router.get("/products", response_model=List[ProductRead], summary="Lister tous les produits")
def list_products(db: Session = Depends(get_db)):
    """Retourne la liste de tous les produits avec leurs sources et le meilleur prix."""
    products = db.query(Product).order_by(Product.name.asc()).all()
    return [_build_product_read(p, db) for p in products]


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED, summary="Ajouter un produit")
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    """
    Crée un nouveau produit.
    Si des informations de magasin et d'URL sont fournies, associe immédiatement une première source.
    """
    # 1. Vérifier si un produit avec ce nom existe déjà
    product = db.query(Product).filter(Product.name == payload.name.strip()).first()
    if not product:
        product = Product(name=payload.name.strip())
        db.add(product)
        db.commit()
        db.refresh(product)

    # 2. Si un magasin/URL est fourni, créer ou associer la source
    if payload.store_name and payload.url:
        store_name = payload.store_name.strip()
        store = db.query(Store).filter(Store.name == store_name).first()
        if not store:
            store = Store(name=store_name, url=payload.url)
            db.add(store)
            db.commit()
            db.refresh(store)

        # Vérifier si la source existe déjà
        existing_source = (
            db.query(ProductSource)
            .filter(ProductSource.product_id == product.id, ProductSource.store_id == store.id)
            .first()
        )
        if not existing_source:
            source = ProductSource(
                product_id=product.id,
                store_id=store.id,
                url=payload.url.strip(),
                alert_threshold=payload.alert_threshold
            )
            db.add(source)
            db.commit()

    db.refresh(product)
    return _build_product_read(product, db)


@router.get("/products/{product_id}", response_model=ProductRead, summary="Obtenir les détails d'un produit")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Retourne le produit spécifié par son identifiant avec l'ensemble de ses sources."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return _build_product_read(product, db)


@router.delete("/products/{product_id}", status_code=status.HTTP_200_OK, summary="Supprimer un produit")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Supprime un produit et l'ensemble de ses sources et historiques associés."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    db.delete(product)
    db.commit()
    return {"message": f"Produit '{product.name}' supprimé avec succès"}


@router.post("/products/{product_id}/sources", response_model=ProductSourceRead, summary="Ajouter une source marchande à un produit")
def add_product_source(product_id: int, payload: ProductSourceCreate, db: Session = Depends(get_db)):
    """Permet de surveiller le même produit sur un autre site e-commerce."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    store = db.query(Store).filter(Store.id == payload.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Magasin non trouvé")

    source = ProductSource(
        product_id=product.id,
        store_id=store.id,
        url=payload.url,
        alert_threshold=payload.alert_threshold
    )
    db.add(source)
    db.commit()
    db.refresh(source)

    return {
        "id": source.id,
        "product_id": source.product_id,
        "store_id": source.store_id,
        "store_name": store.name,
        "url": source.url,
        "alert_threshold": source.alert_threshold,
        "current_price": None,
        "last_updated": None
    }


@router.delete("/sources/{source_id}", summary="Supprimer une source marchande")
def delete_product_source(source_id: int, db: Session = Depends(get_db)):
    """Supprime la surveillance d'un magasin pour un produit donné."""
    source = db.query(ProductSource).filter(ProductSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source non trouvée")
    db.delete(source)
    db.commit()
    return {"message": "Source marchande supprimée"}
