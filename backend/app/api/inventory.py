from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.db import get_db
from backend.app.api.auth import get_current_user
from backend.app.models.models import User, Inventory, InventoryLedger
from backend.app.schemas.schemas import InventoryResponse, InventoryLedgerCreate, RestockRequest

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("/status", response_model=list[InventoryResponse])
def get_inventory_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Owner", "InventoryManager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Insufficient permissions."
        )
    return db.query(Inventory).order_by(Inventory.material_name, Inventory.type_spec).all()

@router.get("/alerts", response_model=list[InventoryResponse])
def get_inventory_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Owner", "InventoryManager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Insufficient permissions."
        )
    alerts = db.query(Inventory).filter(
        Inventory.quantity_available < Inventory.safety_threshold
    ).all()
    return alerts

@router.post("/restock/{inventory_id}")
def restock_item(
    inventory_id: int,
    req: RestockRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Owner", "InventoryManager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access Denied.")

    item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    item.quantity_available += req.quantity
    item.last_restocked_at = datetime.utcnow()

    ledger = InventoryLedger(
        inventory_id=inventory_id,
        quantity_change=req.quantity,
        transaction_type="Restock",
        updated_by_user_id=current_user.id
    )
    db.add(ledger)
    db.commit()

    return {
        "message": f"Restocked {req.quantity} units of {item.type_spec}",
        "new_quantity": item.quantity_available,
        "material": item.type_spec
    }

@router.post("/ledger", status_code=status.HTTP_201_CREATED)
def add_ledger_entry(
    entry_in: InventoryLedgerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Owner", "InventoryManager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Insufficient permissions."
        )

    material = db.query(Inventory).filter(Inventory.id == entry_in.inventory_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Inventory material not found")

    new_quantity = material.quantity_available + entry_in.quantity_change
    if new_quantity < 0:
        raise HTTPException(status_code=400, detail="Cannot adjust quantity below zero.")

    ledger = InventoryLedger(
        inventory_id=entry_in.inventory_id,
        quantity_change=entry_in.quantity_change,
        transaction_type=entry_in.transaction_type,
        updated_by_user_id=current_user.id
    )
    material.quantity_available = new_quantity

    db.add(ledger)
    db.commit()

    return {"message": "Inventory ledger transaction recorded successfully", "new_quantity": new_quantity}
