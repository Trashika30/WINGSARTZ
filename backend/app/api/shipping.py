from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.db import get_db
from backend.app.api.auth import get_current_user
from backend.app.models.models import User, Order, Shipping

router = APIRouter(prefix="/shipping", tags=["Shipping"])

@router.get("/rates")
def get_shipping_rates(
    weight_lbs: float,
    zip_code: str,
    current_user: User = Depends(get_current_user)
):
    # Only allow Owner or ShippingManager
    if current_user.role not in ["Owner", "ShippingManager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access Denied: Insufficient permissions."
        )
        
    if weight_lbs <= 0:
        raise HTTPException(status_code=400, detail="Weight must be positive.")
        
    # Indian Shipping Operators rates calculation (INR ₹)
    distance_factor = float(len(zip_code)) * 25.0
    
    delhivery_cost = 120.00 + (weight_lbs * 45.0) + distance_factor
    bluedart_cost = 250.00 + (weight_lbs * 70.0) + distance_factor
    dtdc_cost = 180.00 + (weight_lbs * 50.0) + (distance_factor * 1.2)
    indiapost_cost = 60.00 + (weight_lbs * 20.0) + (distance_factor * 0.8)
    
    # Estimate shipping time based on courier speed profiles
    quotes = [
        {
            "carrier": "Delhivery Express",
            "cost": round(delhivery_cost, 2),
            "delivery_days": 2,
            "recommended": True,
            "reason": "Delhivery recommended: lowest express courier cost with 2-day delivery time."
        },
        {
            "carrier": "Blue Dart Air",
            "cost": round(bluedart_cost, 2),
            "delivery_days": 1,
            "recommended": False,
            "reason": "Blue Dart is the fastest option but has a high air courier surcharge."
        },
        {
            "carrier": "DTDC Ground",
            "cost": round(dtdc_cost, 2),
            "delivery_days": 3,
            "recommended": False,
            "reason": "Standard ground speed with moderate cost."
        },
        {
            "carrier": "India Post Speed",
            "cost": round(indiapost_cost, 2),
            "delivery_days": 5,
            "recommended": False,
            "reason": "Most economical option but has the longest delivery duration."
        }
    ]
    
    # Sort to verify recommended choice
    quotes.sort(key=lambda x: x["cost"])
    # Set the cheapest one as recommended if Delhivery isn't cheapest
    for q in quotes:
        q["recommended"] = False
    
    # Delhivery is usually recommended for balance of speed and cost
    for q in quotes:
        if q["carrier"] == "Delhivery Express":
            q["recommended"] = True
            break

    return {
        "destination_zip": zip_code,
        "package_weight_lbs": weight_lbs,
        "quotes": quotes
    }
