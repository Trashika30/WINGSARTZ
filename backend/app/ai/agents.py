from typing import Dict, Any, List
from backend.app.core.config import settings
from backend.app.ai.rag import rag_engine

def run_openai_call(prompt: str, system_prompt: str) -> str:
    """Helper to execute LLM calls with key verification."""
    if settings.OPENAI_API_KEY == "mock-key-for-development" or not settings.OPENAI_API_KEY:
        raise ValueError("Mock key active")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        raise e

# 1. Customer Support Agent
def customer_support_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    query = state.get("user_query", "")
    context = rag_engine.retrieve_context(query)
    
    system_prompt = "You are WingsArtz Customer Support Agent. Answer questions accurately based only on the provided context."
    prompt = f"Context: {context}\\n\\nQuery: {query}"
    
    try:
        response = run_openai_call(prompt, system_prompt)
    except Exception:
        # Fallback heuristic
        joined_context = " ".join(context)
        response = f"Hello! Based on WingsArtz store policies: {joined_context}. Let me know if I can help you with anything else!"
        
    state["retrieved_context"] = context
    state["final_output"] = response
    return state

# 2. Inventory Risk Agent
def inventory_risk_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    alerts = state.get("inventory_alerts", [])
    recommendations = state.get("recommendations_list", [])
    
    # If we have low stock alert items, generate restock recommendations
    for alert in alerts:
        mat_name = alert.get("material_name", "")
        spec = alert.get("type_spec", "")
        qty = alert.get("quantity_available", 0)
        threshold = alert.get("safety_threshold", 5)
        
        reorder_qty = (threshold * 3) - qty
        rec_text = f"Inventory shortage detected for {spec} ({qty} remaining). Recommend purchasing {reorder_qty} units immediately to avoid fulfillment delays."
        
        recommendations.append({
            "agent_type": "Inventory",
            "recommendation_text": rec_text,
            "confidence_score": 0.95,
            "cost_impact": reorder_qty * 12.50, # mock cost
            "profit_impact": reorder_qty * 25.00,
            "approval_required": True
        })
        
    state["recommendations_list"] = recommendations
    return state

# 3. Demand Prediction Agent
def demand_prediction_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    # Mock forecasting evaluation
    recommendations = state.get("recommendations_list", [])
    
    # We can evaluate seasonal rush based on active month
    recommendations.append({
        "agent_type": "Demand",
        "recommendation_text": "Holiday demand spike predicted for November/December. Suggest increasing canvas and framing inventories by 30% to secure wholesale rates.",
        "confidence_score": 0.88,
        "cost_impact": 650.00,
        "profit_impact": 2200.00,
        "approval_required": True
    })
    
    state["recommendations_list"] = recommendations
    return state

# 4. Shipping Optimization Agent
def shipping_optimization_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    recommendations = state.get("recommendations_list", [])
    
    # Shipping optimization heuristic
    recommendations.append({
        "agent_type": "Shipping",
        "recommendation_text": "Shipping costs to Zone 5 have risen by 12% on FedEx. Propose defaulting Seattle area custom deliveries to UPS Ground to save $3.40 per order.",
        "confidence_score": 0.90,
        "cost_impact": -3.40,
        "profit_impact": 3.40,
        "approval_required": False # low level auto-exec
    })
    
    state["recommendations_list"] = recommendations
    return state

# 5. Business Decision Agent
def business_decision_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    recommendations = state.get("recommendations_list", [])
    active_risks = state.get("active_risks", [])
    
    # Check for painter overload risks
    overloaded = False
    for risk in active_risks:
        if "PainterOverload" in risk.get("risk_type", ""):
            overloaded = True
            
    if overloaded:
        recommendations.append({
            "agent_type": "Business",
            "recommendation_text": "Painter backlog exceeds 12 active custom portrait orders. Recommend hiring 1 temp contractor painter for the next 3 weeks.",
            "confidence_score": 0.92,
            "cost_impact": 1200.00,
            "profit_impact": 3400.00,
            "approval_required": True
        })
        
    state["recommendations_list"] = recommendations
    return state
