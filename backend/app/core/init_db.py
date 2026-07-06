from backend.app.core.db import engine, Base
from backend.app.models.models import User, Order, CustomPortraitSpec, PainterWIPUpload, Inventory, InventoryLedger, Shipping, Payment, AIRecommendation, DemandForecast, RiskAnalysis, AuditLog

def init_db():
    print("Initializing Database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
