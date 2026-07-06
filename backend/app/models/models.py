from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Boolean, Text, func
from sqlalchemy.orm import relationship
from backend.app.core.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False, default="Customer") # Customer, Owner, Painter, InventoryManager, ShippingManager
    status = Column(String(50), nullable=False, default="Active") # Active, Pending, Suspended
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    orders = relationship("Order", back_populates="customer", foreign_keys="Order.customer_id")
    assigned_specs = relationship("CustomPortraitSpec", back_populates="assigned_painter", foreign_keys="CustomPortraitSpec.assigned_painter_id")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    tracking_number = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(String(50), nullable=False, default="Pending") # Pending, Accepted, Painting, Completed, Packed, Shipped, Delivered, Cancelled
    total_price = Column(Numeric(10, 2), nullable=False, default=0.00)
    delivery_date = Column(DateTime(timezone=True), nullable=False)
    location = Column(String(255), nullable=False, default="Anna Nagar, Chennai")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    customer = relationship("User", back_populates="orders", foreign_keys=[customer_id])
    spec = relationship("CustomPortraitSpec", uselist=False, back_populates="order")
    shipping = relationship("Shipping", uselist=False, back_populates="order")
    payment = relationship("Payment", uselist=False, back_populates="order")
    ledger_entries = relationship("InventoryLedger", back_populates="order")

class CustomPortraitSpec(Base):
    __tablename__ = "custom_portrait_specs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False)
    image_url = Column(String(2083), nullable=False)
    custom_description = Column(Text, nullable=False)
    size_inches = Column(String(50), nullable=False) # 8x10, 11x14, 16x20, 24x36
    frame_type = Column(String(100), nullable=False) # None, Black Wood, Oak Wood, Gold Filigree
    assigned_painter_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    order = relationship("Order", back_populates="spec")
    assigned_painter = relationship("User", back_populates="assigned_specs", foreign_keys=[assigned_painter_id])
    wip_uploads = relationship("PainterWIPUpload", back_populates="spec")

class PainterWIPUpload(Base):
    __tablename__ = "painter_wip_uploads"

    id = Column(Integer, primary_key=True, index=True)
    spec_id = Column(Integer, ForeignKey("custom_portrait_specs.id", ondelete="CASCADE"), nullable=False)
    wips_image_url = Column(String(2083), nullable=False)
    comments = Column(Text, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    spec = relationship("CustomPortraitSpec", back_populates="wip_uploads")

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    material_name = Column(String(100), nullable=False) # Canvas, Frame, Paint, Packaging, GiftBox
    type_spec = Column(String(100), nullable=False) # e.g. 16x20 Canvas, Oak Frame
    quantity_available = Column(Integer, nullable=False, default=0)
    safety_threshold = Column(Integer, nullable=False, default=5)
    last_restocked_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    ledger_entries = relationship("InventoryLedger", back_populates="inventory")

class InventoryLedger(Base):
    __tablename__ = "inventory_ledger"

    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id", ondelete="RESTRICT"), nullable=False)
    quantity_change = Column(Integer, nullable=False) # negative for consumption, positive for restock
    transaction_type = Column(String(50), nullable=False) # Restock, Consumption, Adjustment
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    updated_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    inventory = relationship("Inventory", back_populates="ledger_entries")
    order = relationship("Order", back_populates="ledger_entries")

class Shipping(Base):
    __tablename__ = "shipping"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False)
    courier_name = Column(String(100), nullable=False)
    label_url = Column(String(2083), nullable=False)
    shipping_cost = Column(Numeric(10, 2), nullable=False, default=0.00)
    estimated_delivery = Column(DateTime(timezone=True), nullable=False)
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    order = relationship("Order", back_populates="shipping")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False)
    transaction_id = Column(String(255), unique=True, nullable=False)
    payment_gateway = Column(String(50), nullable=False) # Stripe, PayPal
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), nullable=False, default="Pending") # Pending, Success, Failed, Refunded
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="payment")

class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    agent_type = Column(String(50), nullable=False) # Demand, Inventory, Shipping, Business
    recommendation_text = Column(Text, nullable=False)
    confidence_score = Column(Numeric(3, 2), nullable=False)
    cost_impact = Column(Numeric(10, 2), nullable=False, default=0.00)
    profit_impact = Column(Numeric(10, 2), nullable=False, default=0.00)
    approval_required = Column(Boolean, nullable=False, default=True)
    status = Column(String(50), nullable=False, default="Pending") # Pending, Approved, Rejected, Executed
    approved_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DemandForecast(Base):
    __tablename__ = "demand_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    target_period_start = Column(DateTime(timezone=True), nullable=False)
    target_period_end = Column(DateTime(timezone=True), nullable=False)
    forecasting_type = Column(String(50), nullable=False) # Weekly, Monthly, Festival, Holiday
    expected_orders = Column(Integer, nullable=False)
    expected_revenue = Column(Numeric(10, 2), nullable=False)
    recommended_workforce_adjustment = Column(String(255), nullable=True)
    recommended_materials = Column(Text, nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

class RiskAnalysis(Base):
    __tablename__ = "risk_analysis"

    id = Column(Integer, primary_key=True, index=True)
    risk_type = Column(String(100), nullable=False)
    probability = Column(Numeric(3, 2), nullable=False)
    impact = Column(Numeric(3, 2), nullable=False)
    severity = Column(String(50), nullable=False) # Low, Medium, High, Critical
    suggested_mitigation = Column(Text, nullable=False)
    approved_mitigation = Column(Boolean, nullable=False, default=False)
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action_taken = Column(String(255), nullable=False)
    affected_table = Column(String(100), nullable=False)
    record_id = Column(Integer, nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
