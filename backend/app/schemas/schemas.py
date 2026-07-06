from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: int
    role: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Custom Portrait Schemas
class CustomPortraitCreate(BaseModel):
    size_inches: str = Field(..., description="8x10, 11x14, 16x20, 24x36")
    frame_type: str = Field(..., description="None, Black Wood, Oak Wood, Gold Filigree")
    custom_description: str = Field(..., min_length=10)
    delivery_date: datetime

# Order Schemas
class OrderResponse(BaseModel):
    id: int
    tracking_number: str
    status: str
    total_price: float
    delivery_date: datetime
    location: str
    created_at: datetime

    class Config:
        from_attributes = True

class PortraitSpecInfo(BaseModel):
    id: int
    size_inches: str
    frame_type: str
    custom_description: str
    image_url: str
    assigned_painter_id: Optional[int] = None

    class Config:
        from_attributes = True

class CustomerInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str

    class Config:
        from_attributes = True

class OrderDetailResponse(BaseModel):
    id: int
    tracking_number: str
    status: str
    total_price: float
    delivery_date: datetime
    location: str
    created_at: datetime
    customer: Optional[CustomerInfo] = None
    spec: Optional[PortraitSpecInfo] = None

    class Config:
        from_attributes = True

class AssignPainterRequest(BaseModel):
    painter_id: int

class OrderStatusUpdate(BaseModel):
    status: str = Field(..., description="Pending, Accepted, Painting, Completed, Packed, Shipped, Delivered, Cancelled")

class WIPUploadResponse(BaseModel):
    id: int
    spec_id: int
    wips_image_url: str
    comments: Optional[str]
    uploaded_at: datetime

    class Config:
        from_attributes = True

# Inventory Schemas
class InventoryResponse(BaseModel):
    id: int
    material_name: str
    type_spec: str
    quantity_available: int
    safety_threshold: int
    last_restocked_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class InventoryLedgerCreate(BaseModel):
    inventory_id: int
    quantity_change: int
    transaction_type: str # Restock, Consumption, Adjustment
    reason: str

class RestockRequest(BaseModel):
    quantity: int = Field(..., gt=0, description="Number of units to restock")

# AI Recommendation Schemas
class AIRecommendationResponse(BaseModel):
    id: int
    agent_type: str
    recommendation_text: str
    confidence_score: float
    cost_impact: float
    profit_impact: float
    approval_required: bool
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Painter Job Schema
class PainterJobResponse(BaseModel):
    id: int
    order_id: int
    size_inches: str
    frame_type: str
    custom_description: str
    image_url: str
    assigned_painter_id: Optional[int] = None

    class Config:
        from_attributes = True

# Chat Schema
class ChatRequest(BaseModel):
    query: str
    role: str = "Customer"

# User list for painter assignment
class PainterListItem(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str

    class Config:
        from_attributes = True
