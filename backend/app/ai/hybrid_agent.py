import json
from sqlalchemy.orm import Session
from backend.app.models.models import Order, Inventory, AIRecommendation, CustomPortraitSpec
from backend.app.ai.llm_provider import call_llm, get_active_provider
from backend.app.ai.rag import rag_engine
from backend.app.ai.memory import memory

def get_database_context(db: Session, role: str, current_user_id: int) -> str:
    """Fetch minimum required DB context based on role."""
    if role == "Admin":
        total_orders = db.query(Order).count()
        active_orders = db.query(Order).filter(Order.status.in_(["Accepted", "Painting", "Completed", "Packed"])).count()
        pending_orders = db.query(Order).filter(Order.status == "Pending").count()
        low_stock = db.query(Inventory).filter(Inventory.quantity_available < Inventory.safety_threshold).all()
        pending_recs = db.query(AIRecommendation).filter(AIRecommendation.status == "Pending").count()
        
        stock_info = ", ".join([f"{i.type_spec} (Qty: {i.quantity_available})" for i in low_stock]) if low_stock else "All stock healthy"
        
        return (
            f"[DB Context] Total Orders: {total_orders}, Active: {active_orders}, Pending: {pending_orders}. "
            f"Low Stock Items: {stock_info}. Pending AI Recommendations: {pending_recs}."
        )
    elif role == "Painter":
        jobs = db.query(CustomPortraitSpec).filter(CustomPortraitSpec.assigned_painter_id == current_user_id).all()
        if not jobs:
            return "[DB Context] No active assignments."
        job_info = "; ".join([f"Order #{j.order_id}: {j.size_inches}, {j.frame_type}" for j in jobs])
        return f"[DB Context] Assigned Jobs: {job_info}"
    return "[DB Context] Not applicable for this role."

def call_mock_shipping_api() -> str:
    return "[Shipping API] Delhivery Express: Rs. 450 (2-3 days). Blue Dart Air: Rs. 700 (1-2 days). India Post: Rs. 250 (4-7 days)."

def call_mock_weather_api() -> str:
    return "[Weather API] High humidity in Chennai (85%). Drying times for oil paints extended by 24 hours."

def detect_intent(query: str, history_str: str) -> dict:
    """Uses LLM to detect intent and route to tools."""
    prompt = f"""
    Analyze the user's query and conversation history to determine their intent.
    Return a JSON object with:
    - 'intent': One of [GENERAL, DATABASE, STRATEGY, TOOL_SHIPPING, TOOL_WEATHER, RAG_POLICY]
    
    Query: {query}
    History: {history_str}
    
    Respond ONLY with valid JSON.
    """
    try:
        response = call_llm("You are an intent detection router.", prompt)
        if response and "{" in response and "}" in response:
            json_str = response[response.find("{"):response.rfind("}")+1]
            return json.loads(json_str)
    except Exception:
        pass
    
    # Fallback keyword detection if LLM JSON fails
    q = query.lower()
    if any(k in q for k in ["order", "stock", "pending", "inventory", "assign", "how many"]):
        return {"intent": "DATABASE"}
    if any(k in q for k in ["strategy", "improve", "sales", "marketing", "grow", "recommend"]):
        return {"intent": "STRATEGY"}
    if any(k in q for k in ["ship", "courier", "delivery rate", "delhivery"]):
        return {"intent": "TOOL_SHIPPING"}
    if any(k in q for k in ["weather", "humidity", "rain", "dry"]):
        return {"intent": "TOOL_WEATHER"}
    if any(k in q for k in ["policy", "refund", "how long", "turnaround", "acrylic", "oil", "canvas"]):
        return {"intent": "RAG_POLICY"}
    
    return {"intent": "GENERAL"}

def run_hybrid_agent(query: str, role: str, user_id: int, db: Session) -> dict:
    history_str = memory.format_history(user_id)
    
    # 1. Intent Detection
    routing = detect_intent(query, history_str)
    intent = routing.get("intent", "GENERAL")
    
    context_gathered = []
    
    # 2. Tool Routing
    if intent in ["DATABASE", "STRATEGY"]:
        context_gathered.append(get_database_context(db, role, user_id))
    
    if intent in ["TOOL_SHIPPING", "STRATEGY"]:
        context_gathered.append(call_mock_shipping_api())
        
    if intent == "TOOL_WEATHER":
        context_gathered.append(call_mock_weather_api())
        
    if intent in ["RAG_POLICY", "GENERAL", "STRATEGY"]:
        rag_context = rag_engine.retrieve_context(query)
        if rag_context:
            if isinstance(rag_context, list):
                context_gathered.append("[Policy Context] " + " ".join(rag_context))
            else:
                context_gathered.append("[Policy Context] " + str(rag_context))

    # 3. Final Generation
    system_prompt = f"""You are the WingsArtz {role} AI Assistant.
Analyze, reason, and generate the final response.
Use context for personalized answers.
CRITICAL: Be extremely concise to minimize output tokens. Avoid conversational filler, intros, or outtros.
Keep response crisp, professional, and well-formatted using brief bullet points.
Respond in ₹ where applicable.
"""
    
    final_prompt = f"""
Conversation History:
{history_str}

Gathered Context:
{" | ".join(context_gathered) if context_gathered else "No specific external context needed."}

User Query: {query}
"""
    
    response = call_llm(system_prompt, final_prompt)
    if not response:
        response = "I'm currently unable to generate a response. Please try again later."
        
    # Add to memory
    memory.add_message(user_id, "user", query)
    memory.add_message(user_id, "assistant", response)
    
    return {
        "response": response,
        "retrieved_context": context_gathered,
        "agent": f"WingsArtz Hybrid {role} Assistant ({get_active_provider()})"
    }
