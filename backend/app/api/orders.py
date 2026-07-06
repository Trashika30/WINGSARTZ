import os
import shutil
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.db import get_db
from backend.app.api.auth import get_current_user
from backend.app.models.models import User, Order, CustomPortraitSpec, PainterWIPUpload, Shipping
from backend.app.schemas.schemas import OrderResponse, OrderDetailResponse, WIPUploadResponse

router = APIRouter(prefix="/orders", tags=["Orders"])

# Ensure local uploads directory exists
UPLOAD_DIR = "backend/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

SIZE_PRICES = {
    "8x10": 6000.00,
    "11x14": 8000.00,
    "16x20": 10000.00,
    "24x36": 14000.00
}

FRAME_PRICES = {
    "None": 0.00,
    "Black Wood": 1200.00,
    "Oak Wood": 1500.00,
    "Gold Filigree": 2500.00
}

def generate_tracking_number(db: Session) -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    count = db.query(Order).count()
    return f"WA-{date_str}-{count + 1:04d}"

@router.post("/custom", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_custom_order(
    image: UploadFile = File(...),
    size_inches: str = Form(...),
    frame_type: str = Form(...),
    custom_description: str = Form(...),
    delivery_date_str: str = Form(...),
    location: str = Form("Anna Nagar, Chennai"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Customer":
        raise HTTPException(status_code=403, detail="Only customers can place orders.")
    if size_inches not in SIZE_PRICES:
        raise HTTPException(status_code=400, detail="Invalid size option")
    if frame_type not in FRAME_PRICES:
        raise HTTPException(status_code=400, detail="Invalid frame option")

    try:
        delivery_date = datetime.fromisoformat(delivery_date_str.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, use ISO string")

    if delivery_date < datetime.utcnow() + timedelta(days=7):
        raise HTTPException(status_code=400, detail="Custom portrait orders require at least 7 days lead time.")

    if image.content_type not in ["image/jpeg", "image/png", "image/jpg", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, JPEG, PNG, WEBP allowed.")

    file_extension = os.path.splitext(image.filename)[1] if image.filename else ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store file: {str(e)}")

    image_url = f"/static/uploads/{unique_filename}"
    total_price = SIZE_PRICES[size_inches] + FRAME_PRICES[frame_type]
    tracking_num = generate_tracking_number(db)

    new_order = Order(
        customer_id=current_user.id,
        tracking_number=tracking_num,
        status="Pending",
        total_price=total_price,
        delivery_date=delivery_date,
        location=location
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    new_spec = CustomPortraitSpec(
        order_id=new_order.id,
        image_url=image_url,
        custom_description=custom_description,
        size_inches=size_inches,
        frame_type=frame_type
    )
    db.add(new_spec)
    db.commit()

    return new_order

@router.get("/track/{tracking_num}", response_model=OrderResponse)
def get_order_tracking(tracking_num: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.tracking_number == tracking_num).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/my-orders", response_model=List[OrderDetailResponse])
def get_my_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = db.query(Order).filter(Order.customer_id == current_user.id).order_by(Order.created_at.desc()).all()
    return orders

@router.get("/shipping/ready")
def get_orders_ready_for_shipping(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns orders in Completed state, ready to be packed and shipped."""
    if current_user.role not in ["Owner", "ShippingManager"]:
        raise HTTPException(status_code=403, detail="Access Denied.")
    orders = db.query(Order).filter(Order.status.in_(["Completed", "Packed"])).all()
    result = []
    for order in orders:
        spec = db.query(CustomPortraitSpec).filter(CustomPortraitSpec.order_id == order.id).first()
        result.append({
            "id": order.id,
            "tracking_number": order.tracking_number,
            "status": order.status,
            "total_price": float(order.total_price),
            "delivery_date": order.delivery_date.isoformat(),
            "size_inches": spec.size_inches if spec else "N/A",
            "frame_type": spec.frame_type if spec else "N/A"
        })
    return result

@router.post("/shipping/{order_id}/mark-shipped")
def mark_order_shipped(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Owner", "ShippingManager"]:
        raise HTTPException(status_code=403, detail="Access Denied.")
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = "Shipped"
    db.commit()
    return {"message": f"Order {order.tracking_number} marked as Shipped", "status": "Shipped"}

@router.post("/{order_id}/pay")
def pay_for_accepted_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Customer":
        raise HTTPException(status_code=403, detail="Only customers can pay for orders.")
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this order.")
    if order.status != "Accepted":
        raise HTTPException(status_code=400, detail="Only accepted orders can be paid for.")
    
    order.status = "Painting"
    
    from backend.app.models.models import Payment
    payment = Payment(
        order_id=order.id,
        transaction_id=f"TXN-{uuid.uuid4().hex[:8].upper()}",
        payment_gateway="Stripe",
        amount=order.total_price,
        status="Success"
    )
    db.add(payment)
    db.commit()
    db.refresh(order)
    return {"message": "Payment successful. The artist has been notified to commence painting!", "status": order.status}

