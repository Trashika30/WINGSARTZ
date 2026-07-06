from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from backend.app.core.db import get_db
from backend.app.api.auth import get_current_user
from backend.app.models.models import (
    User, Order, CustomPortraitSpec, AIRecommendation,
    RiskAnalysis, Inventory, InventoryLedger
)
from backend.app.schemas.schemas import (
    AIRecommendationResponse, OrderDetailResponse,
    AssignPainterRequest, OrderStatusUpdate, PainterListItem,
    InventoryResponse, RestockRequest
)

router = APIRouter(prefix="/admin", tags=["Owner Administration"])

# ────────────────────────────────────────────────────────────
# KPI DASHBOARD
# ────────────────────────────────────────────────────────────
@router.get("/kpis")
def get_business_kpis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner role required.")

    total_orders = db.query(Order).count()
    revenue_sum = db.query(func.sum(Order.total_price)).scalar() or 0.00
    pending_recs = db.query(AIRecommendation).filter(AIRecommendation.status == "Pending").count()
    active_painters = db.query(User).filter(User.role == "Painter", User.status == "Active").count()
    total_customers = db.query(User).filter(User.role == "Customer").count()
    pending_orders = db.query(Order).filter(Order.status == "Pending").count()
    painting_orders = db.query(Order).filter(Order.status == "Painting").count()
    shipped_orders = db.query(Order).filter(Order.status == "Shipped").count()
    profit = float(revenue_sum) * 0.40

    return {
        "total_orders": total_orders,
        "total_revenue": float(revenue_sum),
        "net_profit": round(profit, 2),
        "pending_recommendations_count": pending_recs,
        "active_painters_count": active_painters,
        "total_customers": total_customers,
        "pending_orders": pending_orders,
        "painting_orders": painting_orders,
        "shipped_orders": shipped_orders
    }

# ────────────────────────────────────────────────────────────
# ORDERS MANAGEMENT
# ────────────────────────────────────────────────────────────
@router.get("/orders", response_model=List[OrderDetailResponse])
def get_all_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner role required.")
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return orders

@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner role required.")

    valid_statuses = ["Pending", "Accepted", "Painting", "Completed", "Packed", "Shipped", "Delivered", "Cancelled"]
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Valid: {valid_statuses}")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = update.status
    db.commit()
    return {"message": f"Order {order.tracking_number} status updated to {update.status}", "status": update.status}

@router.post("/orders/{order_id}/assign-painter")
def assign_painter_to_order(
    order_id: int,
    req: AssignPainterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner role required.")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    painter = db.query(User).filter(User.id == req.painter_id, User.role == "Painter").first()
    if not painter:
        raise HTTPException(status_code=404, detail="Painter not found")

    spec = db.query(CustomPortraitSpec).filter(CustomPortraitSpec.order_id == order_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Portrait spec not found for this order")

    spec.assigned_painter_id = req.painter_id
    spec.assigned_at = datetime.utcnow()

    # Auto-update order to Accepted
    if order.status == "Pending":
        order.status = "Accepted"

    db.commit()
    return {
        "message": f"Painter {painter.first_name} {painter.last_name} assigned to order {order.tracking_number}",
        "order_status": order.status
    }

# ────────────────────────────────────────────────────────────
# PAINTER LIST
# ────────────────────────────────────────────────────────────
@router.get("/painters", response_model=List[PainterListItem])
def get_painters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner role required.")
    return db.query(User).filter(User.role == "Painter", User.status == "Active").all()

# ────────────────────────────────────────────────────────────
# AI RECOMMENDATIONS
# ────────────────────────────────────────────────────────────
@router.get("/recommendations", response_model=List[AIRecommendationResponse])
def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner role required.")
    return db.query(AIRecommendation).order_by(AIRecommendation.created_at.desc()).all()

@router.post("/recommendations/{rec_id}/approve")
def approve_recommendation(
    rec_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner role required.")

    rec = db.query(AIRecommendation).filter(AIRecommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    if rec.status != "Pending":
        raise HTTPException(status_code=400, detail="Recommendation already processed.")

    rec.status = "Approved"
    rec.approved_by_user_id = current_user.id

    executed_action = ""
    if "Canvas" in rec.recommendation_text or "canvas" in rec.recommendation_text:
        canvas_item = db.query(Inventory).filter(Inventory.type_spec.like("%Canvas%")).first()
        if canvas_item:
            canvas_item.quantity_available += 20
            canvas_item.last_restocked_at = datetime.utcnow()
            executed_action = f"Auto-restocked: Added 20 units to {canvas_item.type_spec}."
    else:
        executed_action = "Strategy approved and logged."

    db.commit()
    return {"message": "Recommendation approved", "status": "Approved", "action_taken": executed_action}

@router.post("/recommendations/{rec_id}/reject")
def reject_recommendation(
    rec_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner role required.")

    rec = db.query(AIRecommendation).filter(AIRecommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    if rec.status != "Pending":
        raise HTTPException(status_code=400, detail="Recommendation already processed.")

    rec.status = "Rejected"
    db.commit()
    return {"message": "Recommendation rejected", "status": "Rejected"}

# ────────────────────────────────────────────────────────────
# INVENTORY MANAGEMENT (Owner access)
# ────────────────────────────────────────────────────────────
@router.post("/inventory/{inventory_id}/restock")
def restock_inventory_item(
    inventory_id: int,
    req: RestockRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Owner", "InventoryManager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

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
        "new_quantity": item.quantity_available
    }
