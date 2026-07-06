from typing import Dict, Any, List
from backend.app.ai.agents import (
    customer_support_agent,
    inventory_risk_agent,
    demand_prediction_agent,
    shipping_optimization_agent,
    business_decision_agent
)

# Define GraphState schema structure
class GraphState:
    def __init__(self):
        self.state = {
            "user_query": "",
            "user_role": "",
            "user_id": 0,
            "retrieved_context": [],
            "inventory_alerts": [],
            "active_risks": [],
            "recommendations_list": [],
            "final_output": "",
            "next_node": ""
        }

def run_agentic_workflow(
    query: str, 
    role: str = "Customer", 
    user_id: int = 0,
    inventory_alerts: List[Dict[str, Any]] = None,
    active_risks: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Simulates the LangGraph multi-agent traversal.
    1. Router splits task based on query/events.
    2. Customer Chat queries RAG.
    3. Cron jobs route stock anomalies to Inventory Risk and Business agents.
    """
    # Initialize state
    state = {
        "user_query": query,
        "user_role": role,
        "user_id": user_id,
        "retrieved_context": [],
        "inventory_alerts": inventory_alerts or [],
        "active_risks": active_risks or [],
        "recommendations_list": [],
        "final_output": "",
        "next_node": ""
    }
    
    # Simple Router edge logic
    if role == "Customer" or "chat" in query.lower() or "help" in query.lower() or "policy" in query.lower():
        # Route to Customer Support (RAG)
        state = customer_support_agent(state)
    else:
        # Route to Admin Audits
        # Run forecast predictions
        state = demand_prediction_agent(state)
        # Check stock risks
        if state["inventory_alerts"]:
            state = inventory_risk_agent(state)
        # Run shipping routing optimizations
        state = shipping_optimization_agent(state)
        # Run business strategic scaling decisions
        if state["active_risks"]:
            state = business_decision_agent(state)
            
    return state

# LangGraph compilation block (attempt compile, fallback to Python class wrapper)
try:
    from langgraph.graph import StateGraph, END
    
    workflow = StateGraph(dict) # TypedDict GraphState
    
    # Register Nodes
    workflow.add_node("support", customer_support_agent)
    workflow.add_node("inventory", inventory_risk_agent)
    workflow.add_node("demand", demand_prediction_agent)
    workflow.add_node("shipping", shipping_optimization_agent)
    workflow.add_node("business", business_decision_agent)
    
    # Configure Router Conditional Edges
    def route_decision(state: dict):
        if state.get("user_role") == "Customer":
            return "support"
        return "demand"
        
    workflow.set_conditional_entry_point(
        route_decision,
        {
            "support": "support",
            "demand": "demand"
        }
    )
    
    # Configure sequence paths
    workflow.add_edge("demand", "inventory")
    workflow.add_edge("inventory", "shipping")
    workflow.add_edge("shipping", "business")
    workflow.add_edge("business", END)
    workflow.add_edge("support", END)
    
    compiled_graph = workflow.compile()
    print("LangGraph StateGraph compiled successfully!")
except Exception as e:
    print(f"LangGraph not compiled directly due to environment restrictions: {e}. Utilizing standard Python Router class wrapper.")
    compiled_graph = None
