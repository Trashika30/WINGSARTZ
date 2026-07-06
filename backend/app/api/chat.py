from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.core.db import get_db
from backend.app.core.config import settings
from backend.app.ai.graph import run_agentic_workflow
from backend.app.api.auth import get_current_user
from backend.app.models.models import User, Order, Inventory, AIRecommendation, CustomPortraitSpec
from backend.app.ai.rag import rag_engine
from backend.app.ai.llm_provider import call_llm, get_active_provider
from backend.app.ai.hybrid_agent import run_hybrid_agent

router = APIRouter(prefix="/chat", tags=["AI Conversational Chatbots"])

class ChatRequest(BaseModel):
    query: str
    role: str = "Customer"


def smart_response(query: str, rules: dict, default_response: str) -> str:
    """
    Matches user query against keyword rules in priority order.
    Returns the first matching rule response, or the default if nothing matches.
    Each rule key can be a comma-separated list of synonyms.
    """
    query_lower = query.lower().strip()

    # Greeting shortcut — check before everything
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon",
                 "good evening", "howdy", "hiya", "greetings", "sup", "what's up"]
    if any(query_lower == g or query_lower.startswith(g + " ") for g in greetings):
        return rules.get("__greeting__", default_response)

    # Capability / help shortcut
    help_triggers = ["what can you do", "help me", "what do you know",
                     "capabilities", "what can i ask", "what should i ask"]
    if any(t in query_lower for t in help_triggers):
        return rules.get("__help__", default_response)

    # Match any rule whose keywords appear in the query
    for key, response in rules.items():
        if key.startswith("__"):
            continue
        keywords = [k.strip() for k in key.split(",")]
        if any(kw in query_lower for kw in keywords):
            return response

    return default_response


# ────────────────────────────────────────────────────────────
# CUSTOMER SUPPORT CHATBOT
# ────────────────────────────────────────────────────────────
@router.post("/support")
def chat_support(req: ChatRequest, db: Session = Depends(get_db)):
    """RAG-powered customer support chat endpoint using OpenAI ChatGPT or smart fallback."""
    retrieved = rag_engine.retrieve_context(req.query)

    system_prompt = (
        "You are the WingsArtz Storefront Customer Support Assistant.\n"
        "Answer customer questions about sizing, framing, refunds, shipping, and order tracking.\n"
        "Keep responses concise and friendly. Format key info in bullet points.\n"
        f"WingsArtz Policies & Guidelines:\n{retrieved}\n"
        "Always respond in Indian Rupees (₹)."
    )

    llm_response = call_llm(system_prompt, req.query)
    if llm_response:
        return {
            "response": llm_response,
            "retrieved_context": retrieved,
            "agent": f"WingsArtz Customer Support ({get_active_provider()})"
        }

    fallback_rules = {
        "__greeting__": (
            "👋 **Welcome to WingsArtz Customer Support!**\n\n"
            "I can help you with:\n"
            "• 🎨 **Portrait Sizes & Pricing** — ask \"What are your prices?\"\n"
            "• 🖼️ **Framing Options** — ask \"What frames do you offer?\"\n"
            "• 🚚 **Shipping & Delivery** — ask \"How long does delivery take?\"\n"
            "• 💰 **Refund Policy** — ask \"What is your refund policy?\"\n"
            "• 📦 **Order Process** — ask \"How does the order process work?\"\n"
            "• 🖌️ **Painting Care** — ask \"How do I care for my painting?\"\n\n"
            "What would you like to know? 😊"
        ),
        "__help__": (
            "🤖 **Here's what I can help you with:**\n\n"
            "• Portrait size options and prices (₹6,000 – ₹14,000)\n"
            "• Frame upgrades (None / Black Wood / Oak Wood / Gold Filigree)\n"
            "• Shipping couriers and delivery timelines\n"
            "• Refund and cancellation policy\n"
            "• How custom portrait orders work step-by-step\n"
            "• Painting care and durability tips\n\n"
            "Just type your question and I'll answer right away! 🎨"
        ),
        "refund,cancel,money back": (
            "💰 **WingsArtz Refund Policy:**\n\n"
            "• **Pending status:** 100% refund if cancelled within 24 hours of placing the order.\n"
            "• **Accepted / Painting status:** Maximum 50% refund — materials and painter time have been allocated.\n"
            "• **Completed / Shipped status:** No refunds once the portrait is dispatched.\n"
            "• **Damaged in transit:** Full replacement or 100% refund with photographic proof within 48 hours of delivery."
        ),
        "price,cost,how much,rate,charge,fee": (
            "🎨 **WingsArtz Portrait Sizes & Pricing (INR):**\n\n"
            "| Size | Price |\n"
            "|------|-------|\n"
            "| 8\" × 10\" (Small) | ₹6,000 |\n"
            "| 11\" × 14\" (Medium) | ₹8,000 |\n"
            "| 16\" × 20\" (Standard) | ₹10,000 |\n"
            "| 24\" × 36\" (Extra Large) | ₹14,000 |\n\n"
            "**Frame add-ons:** None (₹0) | Black Wood (+₹1,200) | Oak Wood (+₹1,500) | Gold Filigree (+₹2,500)\n\n"
            "📦 Delivery charges are added at checkout based on courier selection."
        ),
        "frame,wood,filigree,framing": (
            "🖼️ **WingsArtz Framing Options (INR):**\n\n"
            "• **No Frame** — ₹0 (canvas rolled or flat-packed)\n"
            "• **Black Solid Wood Frame** — ₹1,200\n"
            "• **Oak Natural Wood Frame** — ₹1,500\n"
            "• **Premium Gold Filigree Frame** — ₹2,500\n\n"
            "⏱️ Frames require **2 additional working days** for assembly and drying before dispatch."
        ),
        "shipping,delivery,dispatch,courier,send": (
            "🚚 **WingsArtz Shipping & Delivery:**\n\n"
            "• **India Post Speed Post** — ₹270 | 4–7 days\n"
            "• **Delhivery Ground** — ₹350 | 4–6 days *(Best value for metros)*\n"
            "• **Delhivery Express** — ₹472.50 | 2–3 days *(Recommended)*\n"
            "• **DTDC Ground** — ₹585 | 4–7 days\n"
            "• **Blue Dart Air** — ₹715 | 1–2 days *(Best for urgent/fragile frames)*\n\n"
            "📍 We deliver across all of India. A tracking number is sent once dispatched."
        ),
        "how long,time,days,turnaround,when": (
            "⏱️ **WingsArtz Order Turnaround Time:**\n\n"
            "• **Standard portrait** — 7 to 10 working days from acceptance\n"
            "• **Rush order** (surcharge applies) — 3 to 5 working days\n"
            "• **Bulk order** (3+ portraits) — 12 to 15 working days\n"
            "• **Framed portraits** — add 2 extra days for assembly\n\n"
            "🎄 *October–January holiday season:* Add 3–5 extra days due to high demand."
        ),
        "care,durable,clean,maintain,protect,longevity": (
            "🖌️ **Painting Care & Durability Tips:**\n\n"
            "• **Acrylic paintings** last 50–100 years if maintained properly.\n"
            "• **Oil paintings** take 2–6 months to fully dry — do not cover until dry.\n"
            "• ❌ Avoid: direct sunlight, humidity, moisture, and chemical solvents.\n"
            "• ✅ Cleaning: dust gently with a soft, dry brush only.\n"
            "• 📦 Storage: upright in a cool, dry location — never stack face-to-face."
        ),
        "order,process,step,how does,how do": (
            "📋 **WingsArtz Custom Portrait Order Process:**\n\n"
            "1. 📸 Submit your order with reference photo, size, frame, and delivery address.\n"
            "2. ✅ Owner reviews and accepts (usually within 12 hours).\n"
            "3. 💳 You receive a notification and proceed to payment.\n"
            "4. 🎨 Owner assigns a qualified painter.\n"
            "5. 🖌️ Painter creates your portrait and uploads progress photos.\n"
            "6. 👁️ Owner reviews and approves completed artwork.\n"
            "7. 📦 Painting is securely packaged and handed to the courier.\n"
            "8. 🚚 You receive tracking number and monitor delivery."
        ),
        "track,tracking,status,where is": (
            "🔍 **How to Track Your Order:**\n\n"
            "• Go to the **Track Order** page and enter your tracking number (format: WA-YYYYMMDD-XXXX).\n"
            "• You'll see a live status bar: Pending → Accepted → Painting → Completed → Shipped → Delivered.\n"
            "• WIP (work-in-progress) photos uploaded by your painter are visible here.\n\n"
            "📧 You also receive automatic email notifications at each major status change."
        ),
        "size,dimension,inches,canvas,big,small,large": (
            "📐 **Available Portrait Sizes:**\n\n"
            "• **8\" × 10\"** — Small (ideal for desk display)\n"
            "• **11\" × 14\"** — Medium (most gifted size)\n"
            "• **16\" × 20\"** — Standard *(most popular)*\n"
            "• **24\" × 36\"** — Extra Large (statement wall art)\n\n"
            "All portraits are painted on premium cotton (up to 16×20) or linen canvas (24×36)."
        ),
    }

    default_response = (
        "👋 I'm the WingsArtz Customer Support Assistant!\n\n"
        "I can help you with pricing, frame options, delivery times, refund policies, and order tracking.\n\n"
        "Try asking:\n"
        "• *\"What are your portrait prices?\"*\n"
        "• *\"How long does delivery take?\"*\n"
        "• *\"What is your refund policy?\"*\n"
        "• *\"How does the order process work?\"*"
    )

    response = smart_response(req.query, fallback_rules, default_response)
    return {
        "response": response,
        "retrieved_context": retrieved,
        "agent": "WingsArtz Customer Support"
    }


# ────────────────────────────────────────────────────────────
# OWNER/ADMIN CHATBOT
# ────────────────────────────────────────────────────────────
@router.post("/admin/chat")
def admin_chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI Dashboard Analytics & Strategy Chatbot using Hybrid LLM + RAG architecture."""
    if current_user.role != "Owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Owner credentials required."
        )

    return run_hybrid_agent(req.query, "Admin", current_user.id, db)


# ────────────────────────────────────────────────────────────
# PAINTER ASSISTANT CHATBOT
# ────────────────────────────────────────────────────────────
@router.post("/painter/chat")
def painter_chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI Assistant to help painters using Hybrid LLM + RAG architecture."""
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


# ────────────────────────────────────────────────────────────
# INVENTORY MANAGER CHATBOT
# ────────────────────────────────────────────────────────────
@router.post("/inventory/chat")
def inventory_chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI Assistant to help inventory managers check stock levels and plan reorders."""
    if current_user.role not in ["InventoryManager", "Owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Inventory Manager or Owner credentials required."
        )

    query_lower = req.query.lower()
    financial_keywords = ["revenue", "profit", "net revenue", "kpi", "margin", "salary", "audit", "financial"]
    if any(keyword in query_lower for keyword in financial_keywords):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Inventory profiles cannot access financial performance metrics."
        )

    # Fetch live inventory
    all_items = db.query(Inventory).all()
    low_items = [i for i in all_items if i.quantity_available < i.safety_threshold]
    healthy_items = [i for i in all_items if i.quantity_available >= i.safety_threshold]

    low_desc = "\n".join([
        f"  🔴 {i.type_spec}: **{i.quantity_available}** units (threshold: {i.safety_threshold}, reorder: {i.safety_threshold * 3})"
        for i in low_items
    ]) if low_items else "  ✅ None"

    healthy_desc = "\n".join([
        f"  ✅ {i.type_spec}: {i.quantity_available} units (threshold: {i.safety_threshold})"
        for i in healthy_items
    ]) if healthy_items else "  None"

    retrieved = rag_engine.retrieve_context(req.query)

    system_prompt = (
        "You are the WingsArtz Inventory Studio Advisor.\n"
        "Help the inventory team manage stock levels, safety thresholds, and explain material properties.\n"
        "Provide crisp, clear reorder quantities in bullet points.\n"
        f"Inventory Stock Status:\n{low_desc}\n"
        f"Policy Context:\n{retrieved}\n"
    )

    llm_response = call_llm(system_prompt, req.query)
    if llm_response:
        return {
            "response": llm_response,
            "retrieved_context": retrieved,
            "agent": f"WingsArtz Inventory ({get_active_provider()})"
        }

    fallback_rules = {
        "__greeting__": (
            f"👋 **Hello, {current_user.first_name}! Welcome to your Inventory Assistant.**\n\n"
            f"**📦 Quick Stock Overview:**\n"
            f"• Total Items Tracked: **{len(all_items)}**\n"
            f"• 🔴 Low Stock Alerts: **{len(low_items)}** item(s) need restocking\n"
            f"• ✅ Healthy Stock: **{len(healthy_items)}** item(s)\n\n"
            "**🔴 Items Requiring Immediate Reorder:**\n"
            f"{low_desc}\n\n"
            "Ask me about stock levels, reorder quantities, materials, or vendor contacts."
        ),
        "__help__": (
            "🤖 **Inventory Assistant — What I Can Help With:**\n\n"
            "• Check which materials are low or critical stock\n"
            "• Calculate reorder quantities (rule: 3× safety threshold)\n"
            "• Explain material properties (cotton vs. linen canvas, paint types)\n"
            "• View full stock status across all items\n"
            "• Vendor contact details\n\n"
            "Try: *\"What needs restocking?\"*, *\"How much canvas should I order?\"*, or *\"Show all stock levels.\"*"
        ),
        "low stock,shortage,alert,critical,reorder,restock,what to order,need to buy": (
            f"🔴 **Low Stock Alert — Items Requiring Reorder:**\n\n"
            f"{low_desc}\n\n"
            "**Reorder Rule:** Order **3× the safety threshold** to maintain a healthy buffer.\n"
            "📧 **Preferred Vendor:** Art House Wholesale India (Chennai) — arthousetrade@gmail.com"
        ),
        "all stock,full inventory,status,overview,what do we have,current levels": (
            f"📦 **Full Inventory Status:**\n\n"
            f"**🔴 Low Stock ({len(low_items)} items):**\n"
            f"{low_desc}\n\n"
            f"**✅ Healthy Stock ({len(healthy_items)} items):**\n"
            f"{healthy_desc}"
        ),
        "canvas,cotton canvas,linen canvas": (
            "🖼️ **Canvas Stock & Specifications:**\n\n"
            + "\n".join([
                f"  • {i.type_spec}: {i.quantity_available} units (safety: {i.safety_threshold})"
                for i in all_items if "canvas" in i.type_spec.lower() or i.material_name.lower() == "canvas"
            ]) +
            "\n\n**Cotton Canvas:** Best for portraits up to 16×20. Affordable, smooth texture.\n"
            "**Linen Canvas:** Professional grade. Preferred for large oil paintings (18×24 and above)."
        ),
        "frame,frames,framing material": (
            "🖼️ **Frame Stock Status:**\n\n"
            + "\n".join([
                f"  • {i.type_spec}: {i.quantity_available} units (safety: {i.safety_threshold})"
                for i in all_items if i.material_name.lower() == "frame"
            ]) +
            "\n\n**Frame assembly:** Add 2 working days per framed order to production time."
        ),
        "paint,acrylic,oil paint,gesso": (
            "🎨 **Paint & Gesso Stock:**\n\n"
            + "\n".join([
                f"  • {i.type_spec}: {i.quantity_available} units (safety: {i.safety_threshold})"
                for i in all_items if i.material_name.lower() in ["paint"]
            ]) +
            "\n\n**Acrylic Paint:** Fast drying (15–30 mins). Water-soluble when wet.\n"
            "**Oil Paint:** Slow drying (24–72 hrs per layer). Requires turpentine or linseed oil."
        ),
        "packaging,box,boxes,shipping box,gift box": (
            "📦 **Packaging Materials Stock:**\n\n"
            + "\n".join([
                f"  • {i.type_spec}: {i.quantity_available} units (safety: {i.safety_threshold})"
                for i in all_items if i.material_name.lower() == "packaging"
            ]) +
            "\n\n**Packaging Standards:**\n"
            "• Small (8×10–11×14): Bubble wrap + small kraft box + corner protectors\n"
            "• Medium (16×20): 2× bubble wrap + medium frame box + foam inserts\n"
            "• Large (18×24–24×36): 3× bubble wrap + double-wall carton + wooden support"
        ),
        "vendor,supplier,contact,order from,buy from": (
            "📧 **Preferred Vendor Details:**\n\n"
            "• **Art House Wholesale India (Chennai)**\n"
            "• Email: arthousetrade@gmail.com\n"
            "• Supplies: Cotton & linen canvas, gesso, acrylic/oil paint sets, brush sets\n\n"
            "**Reorder Quantities Reference:**\n"
            "• Cotton Canvas 16×20: order 30 units when stock < 10\n"
            "• Oak Frames 16×20: order 15 units when stock < 5\n"
            "• Acrylic/Oil Paint Sets: order 10 sets when stock < 3"
        ),
        "thank,thanks,great,good,perfect,ok,cool": (
            f"😊 **You're welcome, {current_user.first_name}!**\n\n"
            "Keeping stock levels healthy ensures our painters never run out of materials. Feel free to ask anything else! 📦"
        ),
    }

    default_response = (
        f"🤔 I didn't quite catch that, {current_user.first_name}.\n\n"
        f"**📦 Current Stock Alerts ({len(low_items)} low):**\n"
        f"{low_desc}\n\n"
        "You can ask me about:\n"
        "• Low stock alerts and reorder quantities\n"
        "• Full inventory status overview\n"
        "• Canvas, frame, paint, or packaging stock\n"
        "• Material properties and usage guidelines\n"
        "• Vendor contacts for restocking"
    )

    response = smart_response(req.query, fallback_rules, default_response)
    return {
        "response": response,
        "retrieved_context": retrieved,
        "agent": "WingsArtz Inventory Assistant"
    }


# ────────────────────────────────────────────────────────────
# SHIPPING MANAGER CHATBOT
# ────────────────────────────────────────────────────────────
@router.post("/shipping/chat")
def shipping_chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI Assistant to help shipping managers compare courier costs and coordinate dispatch."""
    if current_user.role not in ["ShippingManager", "Owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Shipping Manager or Owner credentials required."
        )

    query_lower = req.query.lower()
    financial_keywords = ["revenue", "profit", "net profit", "kpi", "margin", "salary", "audit", "financial"]
    if any(keyword in query_lower for keyword in financial_keywords):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Shipping profiles cannot access financial performance metrics."
        )

    # Fetch orders ready for dispatch
    completed_orders = db.query(Order).filter(Order.status == "Completed").all()
    packed_orders = db.query(Order).filter(Order.status == "Packed").all()
    shipped_orders = db.query(Order).filter(Order.status == "Shipped").count()

    completed_list = "\n".join([
        f"  📦 {o.tracking_number} → {o.location or 'Address on file'}"
        for o in completed_orders[:8]
    ]) if completed_orders else "  ✅ No completed orders waiting for packaging."

    packed_list = "\n".join([
        f"  🚚 {o.tracking_number} → {o.location or 'Address on file'}"
        for o in packed_orders[:8]
    ]) if packed_orders else "  ✅ No orders waiting for courier pickup."

    retrieved = rag_engine.retrieve_context(req.query)

    system_prompt = (
        "You are the WingsArtz Courier & Logistics Optimizer.\n"
        "Help the shipping team find the best courier routes, check delivery addresses, and organize dispatch.\n"
        "Provide crisp suggestions in clear bullet points using Indian Rupees (₹).\n"
        f"Orders ready to pack: {len(completed_orders)} | Orders ready to ship: {len(packed_orders)}\n"
        f"Policy Context:\n{retrieved}\n"
    )

    llm_response = call_llm(system_prompt, req.query)
    if llm_response:
        return {
            "response": llm_response,
            "retrieved_context": retrieved,
            "agent": f"WingsArtz Shipping ({get_active_provider()})"
        }

    fallback_rules = {
        "__greeting__": (
            f"👋 **Hello, {current_user.first_name}! Welcome to your Shipping & Dispatch Assistant.**\n\n"
            f"**📦 Fulfillment Queue Snapshot:**\n"
            f"• Ready to Pack (Completed): **{len(completed_orders)}** order(s)\n"
            f"• Ready to Ship (Packed): **{len(packed_orders)}** order(s)\n"
            f"• Already Shipped Today: **{shipped_orders}** order(s)\n\n"
            "I can help you with:\n"
            "• 🚚 Courier rate comparison (Delhivery, Blue Dart, DTDC, India Post)\n"
            "• 📦 Packaging standards per portrait size\n"
            "• 📋 Orders ready for packing or dispatch\n"
            "• 🗺️ City-specific courier recommendations\n"
            "• 🏷️ Dispatch workflow step-by-step\n\n"
            "What do you need help with today?"
        ),
        "__help__": (
            "🤖 **Shipping Assistant — What I Can Help With:**\n\n"
            "• Compare all courier rates in INR (Delhivery, Blue Dart, DTDC, India Post)\n"
            "• Recommend the best courier based on destination and urgency\n"
            "• View orders ready to pack or dispatch\n"
            "• Packaging standards for small, medium, and large portraits\n"
            "• Step-by-step dispatch workflow\n\n"
            "Try: *\"Which courier for Chennai?\"*, *\"What is ready to ship?\"*, or *\"How to pack a large portrait?\"*"
        ),
        "queue,ready,completed,dispatch,what to ship,pending shipment": (
            f"📋 **Fulfillment Queue:**\n\n"
            f"**📦 Ready to Pack ({len(completed_orders)} orders — status: Completed):**\n"
            f"{completed_list}\n\n"
            f"**🚚 Ready for Courier Pickup ({len(packed_orders)} orders — status: Packed):**\n"
            f"{packed_list}\n\n"
            "Select your courier, generate a label, and update order status to **Shipped** after handover."
        ),
        "courier,rate,price,compare,which courier,recommend": (
            "🚚 **Courier Rate Comparison (INR):**\n\n"
            "| Courier | Rate | ETA | Best For |\n"
            "|---------|------|-----|----------|\n"
            "| India Post Speed Post | ₹270 | 4–7 days | Budget, non-urgent |\n"
            "| Delhivery Ground | ₹350 | 4–6 days | Standard metro orders |\n"
            "| Delhivery Express | ₹472.50 | 2–3 days | ✅ Recommended balance |\n"
            "| DTDC Ground | ₹585 | 4–7 days | Tier-2 city deliveries |\n"
            "| Blue Dart Air | ₹715 | 1–2 days | Urgent + heavy frames |\n\n"
            "💡 **For Gold Filigree / 24×36 frames:** Always use Blue Dart Air for secure transit."
        ),
        "delhivery": (
            "🚛 **Delhivery Shipping Options:**\n\n"
            "• **Delhivery Ground** — ₹350 flat rate | 4–6 days\n"
            "  ✅ Best for standard-size portraits to metro cities (Chennai, Bengaluru, Mumbai, Hyderabad)\n\n"
            "• **Delhivery Express** — ₹472.50 flat rate | 2–3 days\n"
            "  ✅ Best balanced option — recommended for most orders\n\n"
            "📍 Delhivery has excellent coverage across South India including Tamil Nadu, Karnataka, Kerala."
        ),
        "blue dart,bluedart": (
            "✈️ **Blue Dart Air Shipping:**\n\n"
            "• **Rate:** ₹715 flat rate\n"
            "• **Delivery Time:** 1–2 days nationwide\n"
            "• **Best For:** Urgent orders, premium Gold Filigree frames, heavy 24×36 canvases\n"
            "• **Air-safe:** Fully secure for delicate framed paintings\n\n"
            "💡 Use Blue Dart when the customer pays for express delivery or when the order is overdue."
        ),
        "india post,speed post,post office": (
            "📮 **India Post Speed Post:**\n\n"
            "• **Rate:** ₹270 flat rate\n"
            "• **Delivery Time:** 4–7 days\n"
            "• **Best For:** Budget-conscious customers, non-urgent unframed canvases\n"
            "• **Coverage:** Pan-India including remote areas\n\n"
            "⚠️ Not recommended for large or fragile framed portraits — limited transit protection."
        ),
        "dtdc": (
            "🚚 **DTDC Ground Shipping:**\n\n"
            "• **Rate:** ₹585 flat rate\n"
            "• **Delivery Time:** 4–7 days\n"
            "• **Best For:** Tier-2 and Tier-3 city deliveries where Delhivery coverage is limited\n"
            "• **Cities:** Madurai, Coimbatore, Trichy, Kochi, Vizag, Nagpur\n\n"
            "📦 Available for both standard and framed portrait packaging."
        ),
        "pack,packaging,wrap,bubble wrap,how to pack,packing guide": (
            "📦 **WingsArtz Packaging Standards:**\n\n"
            "**All Sizes:**\n"
            "• Wrap in acid-free tissue paper first.\n"
            "• Mark **FRAGILE — DO NOT BEND** on all 4 sides of the outer box.\n\n"
            "**Small (8×10 to 11×14):**\n"
            "• Bubble wrap ×1 layer + small kraft box + corner protectors.\n\n"
            "**Medium (16×20):**\n"
            "• Bubble wrap ×2 layers + medium frame box + foam inserts on all edges.\n\n"
            "**Large (18×24 to 24×36):**\n"
            "• Bubble wrap ×3 layers + heavy-duty double-wall carton + wooden support brackets.\n\n"
            "**Framed paintings:** Add foam corner guards on all 4 frame corners."
        ),
        "workflow,step,process,how to dispatch,dispatch process": (
            "📋 **Dispatch Workflow (Step-by-Step):**\n\n"
            "1. ✅ Review orders in **Completed** status each morning.\n"
            "2. 🚚 Select courier based on weight, destination, and urgency.\n"
            "3. 📦 Package the painting using the size-appropriate packaging guide.\n"
            "4. 🏷️ Label the box with customer name, delivery address, and tracking number.\n"
            "5. 🤝 Hand over to the chosen courier's pickup agent.\n"
            "6. 🖥️ Update order status to **Shipped** in the admin dashboard.\n"
            "7. 📧 Customer receives an automatic tracking notification via email."
        ),
        "chennai,bengaluru,mumbai,hyderabad,madurai,coimbatore,kochi,pune,delhi": (
            "🗺️ **City-Specific Courier Recommendations:**\n\n"
            "• **Chennai, Bengaluru:** Delhivery Ground (₹350) — best coverage and reliability.\n"
            "• **Mumbai, Pune, Delhi:** Delhivery Express (₹472.50) — faster inter-city transit.\n"
            "• **Hyderabad:** Delhivery Express or DTDC (₹585) — depending on zone.\n"
            "• **Madurai, Coimbatore, Kochi:** DTDC Ground (₹585) — better Tier-2 coverage.\n"
            "• **Remote / Rural Areas:** India Post Speed Post (₹270) — widest reach, add 2 extra days."
        ),
        "thank,thanks,great,good,perfect,ok,cool": (
            f"😊 **You're welcome, {current_user.first_name}!**\n\n"
            "Smooth dispatch keeps our customers happy and orders delivered on time. Feel free to ask anything else! 🚚"
        ),
    }

    default_response = (
        f"🤔 I didn't quite understand that, {current_user.first_name}.\n\n"
        f"**📦 Current Fulfillment Queue:**\n"
        f"• Ready to Pack: **{len(completed_orders)}** order(s)\n"
        f"• Ready to Ship: **{len(packed_orders)}** order(s)\n\n"
        "You can ask me about:\n"
        "• Courier rates and recommendations (Delhivery, Blue Dart, DTDC, India Post)\n"
        "• Orders ready for packing or dispatch\n"
        "• Packaging standards for each portrait size\n"
        "• City-specific courier routing\n"
        "• Step-by-step dispatch workflow"
    )

    response = smart_response(req.query, fallback_rules, default_response)
    return {
        "response": response,
        "retrieved_context": retrieved,
        "agent": "WingsArtz Shipping Assistant"
    }


# ────────────────────────────────────────────────────────────
# CRON TRIGGER FOR AI AGENTS RUN
# ────────────────────────────────────────────────────────────
@router.post("/admin/run-agents")
def run_admin_agents(db: Session = Depends(get_db)):
    """Trigger the full LangGraph multi-agent workflow for Owner dashboard recommendations."""
    alerts_raw = db.query(Inventory).filter(
        Inventory.quantity_available < Inventory.safety_threshold
    ).all()

    inventory_alerts = [
        {
            "material_name": item.material_name,
            "type_spec": item.type_spec,
            "quantity_available": item.quantity_available,
            "safety_threshold": item.safety_threshold
        }
        for item in alerts_raw
    ]

    result = run_agentic_workflow(
        query="Run full business audit",
        role="Owner",
        user_id=1,
        inventory_alerts=inventory_alerts,
        active_risks=[{"risk_type": "PainterOverload", "probability": 0.7}]
    )

    # Persist generated recommendations to DB
    saved_count = 0
    for rec in result.get("recommendations_list", []):
        new_rec = AIRecommendation(
            agent_type=rec["agent_type"],
            recommendation_text=rec["recommendation_text"],
            confidence_score=rec["confidence_score"],
            cost_impact=rec["cost_impact"],
            profit_impact=rec["profit_impact"],
            approval_required=rec["approval_required"],
            status="Pending"
        )
        db.add(new_rec)
        saved_count += 1

    db.commit()

    return {
        "message": f"LangGraph workflow complete. {saved_count} recommendation(s) generated.",
        "recommendations": result.get("recommendations_list", [])
    }


# ────────────────────────────────────────────────────────────
# LLM PROVIDER STATUS ENDPOINT
# ────────────────────────────────────────────────────────────
@router.get("/llm-status")
def llm_status():
    """Returns which LLM provider is currently active and the full cascade order."""
    return {
        "active_provider": get_active_provider(),
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "groq_configured": bool(settings.GROQ_API_KEY),
        "openai_configured": bool(
            settings.OPENAI_API_KEY and
            settings.OPENAI_API_KEY != "mock-key-for-development"
        ),
        "cascade_order": [
            "1. Google Gemini 1.5 Flash  (Primary)",
            "2. Groq Llama3-8b-8192      (Fallback — if Gemini fails or key expires)",
            "3. OpenAI GPT-3.5-turbo     (Last resort)",
            "4. Smart Keyword Rules      (Offline — no API needed)"
        ]
    }
