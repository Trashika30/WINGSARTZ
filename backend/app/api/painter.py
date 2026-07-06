import os
import shutil
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from backend.app.core.db import get_db
from backend.app.api.auth import get_current_user
from backend.app.models.models import User, Order, CustomPortraitSpec, PainterWIPUpload

router = APIRouter(prefix="/painter", tags=["Painter Workspace"])

UPLOAD_DIR = "backend/static/uploads"

@router.get("/jobs")
def get_assigned_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Painter", "Owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Insufficient permissions."
        )
    
    # Return specs assigned to this painter
    if current_user.role == "Owner":
        return db.query(CustomPortraitSpec).all()
        
    return db.query(CustomPortraitSpec).filter(CustomPortraitSpec.assigned_painter_id == current_user.id).all()

@router.post("/jobs/{spec_id}/wip")
async def upload_wip(
    spec_id: int,
    comments: str = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Painter", "Owner"]:
        raise HTTPException(status_code=403, detail="Access Denied.")
        
    spec = db.query(CustomPortraitSpec).filter(CustomPortraitSpec.id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Portrait spec not found")
        
    # Check assignment
    if current_user.role == "Painter" and spec.assigned_painter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Order not assigned to you.")
        
    # Save file
    file_extension = os.path.splitext(image.filename)[1]
    unique_filename = f"wip_{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save image")
        
    wip_url = f"/static/uploads/{unique_filename}"
    
    # Record WIP
    wip = PainterWIPUpload(
        spec_id=spec_id,
        wips_image_url=wip_url,
        comments=comments
    )
    
    # Update order state to Painting if not already
    order = db.query(Order).filter(Order.id == spec.order_id).first()
    if order and order.status == "Accepted":
        order.status = "Painting"
        
    db.add(wip)
    db.commit()
    
    return {"message": "WIP image uploaded successfully", "wip_url": wip_url}

@router.post("/jobs/{spec_id}/complete")
def mark_painting_completed(
    spec_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Painter", "Owner"]:
        raise HTTPException(status_code=403, detail="Access Denied.")
        
    spec = db.query(CustomPortraitSpec).filter(CustomPortraitSpec.id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Portrait spec not found")
        
    # Check assignment
    if current_user.role == "Painter" and spec.assigned_painter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Order not assigned to you.")
        
    order = db.query(Order).filter(Order.id == spec.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Associated order not found")
        
    order.status = "Completed"
    db.commit()
    
    return {"message": "Order marked as Painting Completed", "status": "Completed"}
