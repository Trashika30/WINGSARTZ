import sys
import os

# Add root folder to sys.path to run locally
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.app.core.db import SessionLocal, Base, engine
from backend.app.core.init_db import init_db
from backend.app.core.security import get_password_hash
from backend.app.models.models import User, Inventory

def seed_database():
    # 1. Create tables
    init_db()
    
    db: Session = SessionLocal()
    try:
        print("Seeding Users...")
        # 2. Add Users if they don't exist
        default_users = [
            {
                "email": "owner@wingsartz.com",
                "password_hash": get_password_hash("WingsOwner2026!"),
                "first_name": "Sarah",
                "last_name": "Owner",
                "role": "Owner",
                "status": "Active"
            },
            {
                "email": "painter1@wingsartz.com",
                "password_hash": get_password_hash("WingsPainter2026!"),
                "first_name": "Jack",
                "last_name": "Painter",
                "role": "Painter",
                "status": "Active"
            },
            {
                "email": "inventory@wingsartz.com",
                "password_hash": get_password_hash("WingsInventory2026!"),
                "first_name": "Marcus",
                "last_name": "Inventory",
                "role": "InventoryManager",
                "status": "Active"
            },
            {
                "email": "shipping@wingsartz.com",
                "password_hash": get_password_hash("WingsShipping2026!"),
                "first_name": "Elena",
                "last_name": "Shipping",
                "role": "ShippingManager",
                "status": "Active"
            },
            {
                "email": "customer@gmail.com",
                "password_hash": get_password_hash("WingsCustomer2026!"),
                "first_name": "Emma",
                "last_name": "Customer",
                "role": "Customer",
                "status": "Active"
            }
        ]
        
        for user_data in default_users:
            exists = db.query(User).filter(User.email == user_data["email"]).first()
            if not exists:
                user = User(**user_data)
                db.add(user)
                print(f"Created user: {user_data['email']}")
        
        db.commit()
        
        print("Seeding Inventory...")
        # 3. Add default materials
        default_materials = [
            {"material_name": "Canvas", "type_spec": "8x10 Cotton Canvas", "quantity_available": 15, "safety_threshold": 5},
            {"material_name": "Canvas", "type_spec": "16x20 Cotton Canvas", "quantity_available": 4, "safety_threshold": 10}, # Triggers Low Stock Alert!
            {"material_name": "Canvas", "type_spec": "24x36 Cotton Canvas", "quantity_available": 8, "safety_threshold": 5},
            {"material_name": "Frame", "type_spec": "Black Frame 16x20", "quantity_available": 6, "safety_threshold": 5},
            {"material_name": "Frame", "type_spec": "Oak Frame 16x20", "quantity_available": 3, "safety_threshold": 5}, # Triggers Low Stock Alert!
            {"material_name": "Frame", "type_spec": "Gold Filigree Frame 16x20", "quantity_available": 8, "safety_threshold": 5},
            {"material_name": "Paint", "type_spec": "Titanium White Paint 75ml", "quantity_available": 18, "safety_threshold": 10},
            {"material_name": "Paint", "type_spec": "Ultramarine Blue Paint 75ml", "quantity_available": 12, "safety_threshold": 10},
            {"material_name": "Packaging", "type_spec": "Premium Gift Box", "quantity_available": 25, "safety_threshold": 10},
            {"material_name": "Packaging", "type_spec": "Medium Kraft Shipping Box", "quantity_available": 30, "safety_threshold": 10}
        ]
        
        for mat_data in default_materials:
            exists = db.query(Inventory).filter(
                Inventory.material_name == mat_data["material_name"],
                Inventory.type_spec == mat_data["type_spec"]
            ).first()
            if not exists:
                mat = Inventory(**mat_data)
                db.add(mat)
                print(f"Created material: {mat_data['type_spec']}")
                
        db.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
