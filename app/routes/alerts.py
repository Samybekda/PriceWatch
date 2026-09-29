from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Alert
from app.schemas import AlertRead

router = APIRouter(tags=["Alertes"])


def _format_alert(alert: Alert) -> dict:
    prod_name = alert.source.product.name if alert.source and alert.source.product else "Produit inconnu"
    store_name = alert.source.store.name if alert.source and alert.source.store else "Magasin inconnu"
    return {
        "id": alert.id,
        "product_source_id": alert.product_source_id,
        "product_name": prod_name,
        "store_name": store_name,
        "price": alert.price,
        "message": alert.message,
        "created_at": alert.created_at,
        "is_read": alert.is_read
    }


@router.get("/alerts", response_model=List[AlertRead], summary="Lister toutes les alertes")
def list_alerts(db: Session = Depends(get_db)):
    """Retourne l'ensemble des alertes générées, classées par date décroissante."""
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).all()
    return [_format_alert(a) for a in alerts]


@router.patch("/alerts/{alert_id}/read", response_model=AlertRead, summary="Marquer une alerte comme lue")
def mark_alert_as_read(alert_id: int, db: Session = Depends(get_db)):
    """Marque une alerte spécifique comme lue."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    alert.is_read = True
    db.commit()
    db.refresh(alert)
    return _format_alert(alert)


@router.delete("/alerts/{alert_id}", status_code=status.HTTP_200_OK, summary="Supprimer une alerte")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Supprime une alerte."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    db.delete(alert)
    db.commit()
    return {"message": "Alerte supprimée avec succès"}
