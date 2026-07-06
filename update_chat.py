import re

with open('backend/app/api/chat.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports for hybrid_agent
if 'from backend.app.ai.hybrid_agent import run_hybrid_agent' not in content:
    content = content.replace(
        'from backend.app.ai.llm_provider import call_llm, get_active_provider',
        'from backend.app.ai.llm_provider import call_llm, get_active_provider\nfrom backend.app.ai.hybrid_agent import run_hybrid_agent'
    )

# Replace admin_chat
admin_start = content.find('@router.post("/admin/chat")')
admin_end = content.find('# ────────────────────────────────────────────────────────────\n# PAINTER ASSISTANT CHATBOT')

new_admin_chat = """@router.post("/admin/chat")
def admin_chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    \"\"\"AI Dashboard Analytics & Strategy Chatbot using Hybrid LLM + RAG architecture.\"\"\"
    if current_user.role != "Owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Owner credentials required."
        )

    return run_hybrid_agent(req.query, "Admin", current_user.id, db)


"""

content = content[:admin_start] + new_admin_chat + content[admin_end:]

# Replace painter_chat
painter_start = content.find('@router.post("/painter/chat")')
painter_end = content.find('# ────────────────────────────────────────────────────────────\n# INVENTORY MANAGER CHATBOT')

new_painter_chat = """@router.post("/painter/chat")
def painter_chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    \"\"\"AI Assistant to help painters using Hybrid LLM + RAG architecture.\"\"\"
    if current_user.role not in ["Painter", "Owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Painter or Owner credentials required."
        )

    # Block financial queries
    query_lower = req.query.lower()
    financial_keywords = ["revenue", "profit", "cost impact", "recommendation", "kpi",
                          "margin", "salary", "audit", "financial", "income"]
    if any(keyword in query_lower for keyword in financial_keywords):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Painter profiles cannot access financial data or owner approvals."
        )

    return run_hybrid_agent(req.query, "Painter", current_user.id, db)


"""

content = content[:painter_start] + new_painter_chat + content[painter_end:]

with open('backend/app/api/chat.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated chat.py successfully.")
