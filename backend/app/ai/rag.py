import os
from backend.app.core.config import settings

# ════════════════════════════════════════════════════════════════════
# WingsArtz Comprehensive Knowledge Base
# Rich domain-specific training data for all chatbot modules
# ════════════════════════════════════════════════════════════════════

KNOWLEDGE_BASE = {

    # ─── CUSTOMER SUPPORT KNOWLEDGE ───
    "refunds": (
        "WingsArtz Refund Policy (Indian Rupees):\n"
        "- PENDING status: 100% refund available if cancelled within 24 hours of placing the order.\n"
        "- ACCEPTED/PAINTING status: Maximum 50% refund once the painter has started work and materials have been allocated.\n"
        "- COMPLETED/SHIPPED status: No refunds after the portrait has been dispatched and handed over to courier.\n"
        "- Damage during shipping: Full replacement or 100% refund if photographic proof of damage is provided within 48 hours of delivery."
    ),

    "pricing": (
        "WingsArtz Portrait Sizes and Pricing (Indian Rupees):\n"
        "- 8 x 10 inches (Small): Rs. 6,000 base price\n"
        "- 11 x 14 inches (Medium-Small): Rs. 8,000 base price\n"
        "- 16 x 20 inches (Standard): Rs. 10,000 base price\n"
        "- 18 x 24 inches (Large): Rs. 12,000 base price\n"
        "- 24 x 36 inches (Extra Large): Rs. 14,000 base price\n"
        "Total price = Base price + Frame cost + Delivery charge.\n"
        "Example: 16x20 standard portrait with Black Wood frame + Delhivery Ground delivery = Rs. 10,000 + Rs. 1,200 + Rs. 350 = Rs. 11,550 total."
    ),

    "framing": (
        "WingsArtz Frame Options and Costs (Indian Rupees):\n"
        "- No Frame: Rs. 0 (canvas only, rolled or flat-packed)\n"
        "- Black Solid Wood Frame: Rs. 1,200\n"
        "- Oak Natural Wood Frame: Rs. 1,500\n"
        "- Walnut Dark Wood Frame: Rs. 1,800\n"
        "- Premium Gold Filigree Frame: Rs. 2,500\n"
        "Notes: Frames require 2 additional working days for assembly and drying before dispatch."
    ),

    "shipping_policy": (
        "WingsArtz Shipping & Delivery Policy (Comprehensive):\n"
        "AVAILABLE COURIERS AND RATES:\n"
        "1. India Post Speed Post: Rs. 270 flat rate | 4-7 business days | Best for budget orders, widest India coverage.\n"
        "2. Delhivery Ground: Rs. 350 flat rate | 4-6 business days | Best for metro cities — Chennai, Bengaluru, Mumbai.\n"
        "3. Delhivery Express: Rs. 472.50 flat rate | 2-3 business days | RECOMMENDED — best balance of cost and speed.\n"
        "4. DTDC Ground: Rs. 585 flat rate | 4-7 business days | Best for Tier-2 cities — Madurai, Coimbatore, Kochi.\n"
        "5. Blue Dart Air: Rs. 715 flat rate | 1-2 business days | Best for urgent orders and fragile Gold Filigree frames.\n"
        "DELIVERY OPTIONS:\n"
        "- Home Delivery: Available across all of India via the couriers above.\n"
        "- Store Pickup: Free, available only for customers in Chennai (Anna Nagar studio).\n"
        "SHIPPING RULES:\n"
        "- Customer must provide complete delivery address including PIN code when placing an order.\n"
        "- All paintings are fully insured during transit.\n"
        "- Tracking number is automatically sent to the customer via email upon dispatch.\n"
        "- Remote and rural areas (not serviceable by Delhivery): India Post is used, adding 2 extra transit days.\n"
        "- Framed paintings 24x36 inch must use Blue Dart Air due to weight and fragility requirements.\n"
        "- South Zone deliveries (Tamil Nadu, Karnataka, Kerala, Andhra, Telangana): Delhivery Express is preferred."
    ),

    "turnaround": (
        "WingsArtz Order Turnaround Time:\n"
        "- Standard orders: 7 to 10 working days from acceptance.\n"
        "- Rush orders (surcharge applies): 3 to 5 working days.\n"
        "- Bulk orders (3 or more portraits): 12 to 15 working days.\n"
        "- Framing adds 2 additional days to all order types.\n"
        "- Holiday season (October to January): Expect 3 to 5 extra days due to high demand."
    ),

    "durability": (
        "WingsArtz Painting Care and Durability:\n"
        "- Acrylic paintings: Extremely durable. Last 50 to 100 years if maintained properly.\n"
        "- Oil paintings: Deep, rich colors. Full drying takes 2 to 6 months. Do not cover until dry.\n"
        "- Keep away from: direct sunlight, moisture, humidity, and chemical solvents.\n"
        "- Cleaning: Gently dust with a soft dry brush. Never use damp cloths or sprays.\n"
        "- Storage: Store upright in a cool, dry location. Avoid stacking paintings face-to-face."
    ),

    "order_process": (
        "WingsArtz Order Journey (Step-by-Step):\n"
        "1. Customer submits a portrait order with reference image, size, frame choice, and delivery address.\n"
        "2. Owner reviews and accepts the order (usually within 12 hours).\n"
        "3. Customer receives notification and proceeds to PAYMENT after acceptance.\n"
        "4. Owner assigns the work to a qualified painter.\n"
        "5. Painter begins the portrait and updates progress.\n"
        "6. Owner reviews the completed painting and approves dispatch.\n"
        "7. Painting is securely packaged and handed to the courier.\n"
        "8. Customer receives tracking number and monitors delivery."
    ),

    # ─── PAINTING TECHNIQUE KNOWLEDGE ───
    "oil_technique": (
        "Oil Portrait Painting Technique Guide:\n"
        "- Canvas Priming: Apply 2 thin coats of oil-grade gesso with a wide flat brush. Sand between layers.\n"
        "- Underpainting: Sketch light outlines using raw umber thinned with turpentine. Let dry 24 hours.\n"
        "- Blocking In: Apply mid-tone shadows first using broad flat strokes wet-on-wet.\n"
        "- Layering: Build from dark to light (glazing). Allow 48 to 72 hours between major layers.\n"
        "- Fine Details: Use a fine round brush for eyes, lips, and hair strands at the final stage.\n"
        "- Varnishing: Apply final varnish only after the painting has fully dried (4 to 8 weeks for oil).\n"
        "- Drying time before framing: Minimum 7 days."
    ),

    "acrylic_technique": (
        "Acrylic Portrait Painting Technique Guide:\n"
        "- Canvas Priming: Apply 2 coats of acrylic gesso. Sand lightly between coats.\n"
        "- Palette Preparation: Use a wet palette to prevent colors from drying too quickly.\n"
        "- Paint Consistency: Mix with water or acrylic medium for glazing; use paint straight for impasto.\n"
        "- Layering Speed: Acrylics dry in 15 to 30 minutes per layer. Work in thin glazes.\n"
        "- Blending: Blend wet-on-wet quickly or use a dry brush technique for soft edges.\n"
        "- Detail Work: Use a 00 or 000 round brush for fine features (eyes, hair highlights).\n"
        "- Drying time before framing: Minimum 24 to 48 hours after final layer."
    ),

    "canvas_preparation": (
        "Canvas Preparation Standards at WingsArtz:\n"
        "- All canvases must be pre-primed with 2 coats of professional-grade gesso before painting.\n"
        "- Cotton canvas is used for portraits up to 16x20 inches.\n"
        "- Linen canvas is used for large format (18x24 and above) for superior texture and longevity.\n"
        "- Stretcher bars must be taut. Use a canvas pliers to stretch evenly before priming.\n"
        "- Border bleed: 1.5 inches on all sides for framed work; 0.5 inches for canvas-only work.\n"
        "- Label each canvas with Order ID on the back before painting begins."
    ),

    "custom_instructions": (
        "WingsArtz Custom Portrait Instructions for Painters:\n"
        "- Read the customer's custom description carefully before beginning.\n"
        "- If the description is unclear, raise a flag to the Owner for clarification.\n"
        "- Match skin tones from reference image: do not use default flesh tones.\n"
        "- Background: Paint as specified in the order. Default is plain cream/ivory if unspecified.\n"
        "- Signature: Paint the WingsArtz studio watermark in bottom-right corner (very light gray).\n"
        "- Quality Check: Compare with the reference image at 50%, 80%, and 100% completion."
    ),

    # ─── INVENTORY KNOWLEDGE ───
    "inventory_management": (
        "WingsArtz Inventory Management Guidelines:\n"
        "- Safety Threshold Policy: When stock drops below the safety threshold, trigger an immediate reorder.\n"
        "- Reorder Quantity: Order 3x the safety threshold to maintain a healthy buffer (e.g., threshold 10 -> order 30 units).\n"
        "- Cotton Canvas (8x10): Safety threshold 5 units. Reorder quantity: 20 units.\n"
        "- Cotton Canvas (16x20): Safety threshold 10 units. Reorder quantity: 30 units.\n"
        "- Linen Canvas (24x36): Safety threshold 5 units. Reorder quantity: 15 units.\n"
        "- Acrylic Paint Sets: Safety threshold 3 sets. Reorder quantity: 10 sets.\n"
        "- Oil Paint Sets: Safety threshold 3 sets. Reorder quantity: 10 sets.\n"
        "- Gesso (1L): Safety threshold 5 bottles. Reorder quantity: 15 bottles.\n"
        "- Brushes (Flat Set): Safety threshold 3 sets. Reorder quantity: 10 sets.\n"
        "- Preferred vendor: Art House Wholesale India (Chennai). Contact: arthousetrade@gmail.com."
    ),

    "material_properties": (
        "WingsArtz Material Properties Reference:\n"
        "- Cotton Canvas: Best for portraits up to 16x20. Affordable, smooth texture, takes acrylic and oil well.\n"
        "- Linen Canvas: Professional-grade. Finer texture, more durable, preferred for large oil paintings.\n"
        "- Gesso: Acrylic-based primer. White gesso for bright backgrounds; gray gesso for neutral underlayers.\n"
        "- Acrylic Paints (Artist Grade): Fast drying (15-30 mins). Permanent once dried. Water-soluble when wet.\n"
        "- Oil Paints: Slow drying (24-72 hrs per layer). Rich depth. Requires turpentine or linseed oil as medium.\n"
        "- Varnish: Applied over finished dry paintings to protect from UV, dust, and moisture."
    ),

    # ─── SHIPPING/COURIER KNOWLEDGE ───
    "courier_comparison": (
        "WingsArtz Indian Courier Comparison Guide — Full Reference (All rates in Indian Rupees):\n"
        "\n"
        "COURIER 1 — INDIA POST SPEED POST:\n"
        "Rate: Rs. 270 flat rate (cheapest option).\n"
        "Delivery Time: 4 to 7 business days.\n"
        "Coverage: Pan-India, best reach in rural and remote areas.\n"
        "Best for: Budget-conscious customers, unframed canvas rolls, non-urgent orders.\n"
        "Limitations: Slower transit, less suitable for large or framed paintings.\n"
        "\n"
        "COURIER 2 — DELHIVERY GROUND:\n"
        "Rate: Rs. 350 flat rate (standard value pick).\n"
        "Delivery Time: 4 to 6 business days.\n"
        "Coverage: Excellent in metro cities — Chennai, Bengaluru, Mumbai, Hyderabad, Delhi, Pune.\n"
        "Best for: Standard portrait orders to major cities.\n"
        "\n"
        "COURIER 3 — DELHIVERY EXPRESS (RECOMMENDED):\n"
        "Rate: Rs. 472.50 flat rate.\n"
        "Delivery Time: 2 to 3 business days.\n"
        "Coverage: All metro cities and most Tier-2 cities.\n"
        "Best for: Most WingsArtz portrait deliveries. Recommended as the default shipping option.\n"
        "AI Suggestion: Delhivery Express is the most balanced option — good price, fast speed, reliable tracking.\n"
        "\n"
        "COURIER 4 — DTDC GROUND:\n"
        "Rate: Rs. 585 flat rate.\n"
        "Delivery Time: 4 to 7 business days.\n"
        "Coverage: Strong in Tier-2 and Tier-3 Indian cities where Delhivery reach is limited.\n"
        "Best for: Orders to Madurai, Coimbatore, Trichy, Kochi, Vizag, Nashik, Nagpur.\n"
        "\n"
        "COURIER 5 — BLUE DART AIR:\n"
        "Rate: Rs. 715 flat rate (premium, fastest).\n"
        "Delivery Time: 1 to 2 business days.\n"
        "Coverage: All major Indian cities and airports.\n"
        "Best for: Urgent orders, Gold Filigree frames, large 24x36 portraits, high-value commissions.\n"
        "Mandatory Use: For 24x36 Gold Filigree framed portraits — always use Blue Dart for secure transit.\n"
        "\n"
        "CITY-SPECIFIC ROUTING GUIDE:\n"
        "- Anna Nagar, Chennai: Delhivery Ground (Rs. 350) or store pickup (free).\n"
        "- Bengaluru: Delhivery Ground (Rs. 350) or Delhivery Express (Rs. 472.50).\n"
        "- Mumbai, Pune: Delhivery Express (Rs. 472.50) — 2-3 day priority.\n"
        "- Hyderabad: Delhivery Express (Rs. 472.50).\n"
        "- Madurai, Coimbatore, Kochi: DTDC Ground (Rs. 585).\n"
        "- Remote / Rural Areas: India Post Speed Post (Rs. 270), add 2 extra transit days."
    ),

    "packaging_guide": (
        "WingsArtz Painting Packaging Standards (Full Guide):\n"
        "STEP 1 — ALL SIZES: Wrap the painting in acid-free tissue paper first to protect the surface.\n"
        "\n"
        "SMALL PORTRAIT (8x10 or 11x14 inches):\n"
        "- 1 layer of bubble wrap around the tissue-wrapped painting.\n"
        "- Place in a small kraft cardboard box.\n"
        "- Add foam corner protectors at all 4 corners.\n"
        "- Recommended courier: Delhivery Ground (Rs. 350) or India Post (Rs. 270).\n"
        "\n"
        "MEDIUM PORTRAIT (16x20 inches — most common):\n"
        "- 2 layers of bubble wrap around the tissue-wrapped painting.\n"
        "- Place in a medium-size frame shipping box.\n"
        "- Add foam inserts on all 4 edges and between painting and box walls.\n"
        "- Recommended courier: Delhivery Express (Rs. 472.50).\n"
        "\n"
        "LARGE PORTRAIT (18x24 or 24x36 inches):\n"
        "- 3 layers of bubble wrap.\n"
        "- Place in heavy-duty double-wall corrugated carton.\n"
        "- Add wooden support brackets inside to prevent crushing.\n"
        "- Recommended courier: Blue Dart Air (Rs. 715) — mandatory for 24x36 Gold Filigree frames.\n"
        "\n"
        "FRAMED PAINTINGS (all sizes):\n"
        "- Add foam corner guards to all 4 frame corners before bubble wrapping.\n"
        "- Use hard cardboard edge protectors along the frame sides.\n"
        "\n"
        "LABELING REQUIREMENTS:\n"
        "- Write FRAGILE — DO NOT BEND on all 4 sides of the outer box.\n"
        "- Attach order tracking number sticker to the top and one side of the box.\n"
        "- Include the customer name and full delivery address on a printed label."
    ),

    "dispatch_workflow": (
        "WingsArtz Dispatch & Fulfillment Step-by-Step Workflow:\n"
        "\n"
        "MORNING QUEUE REVIEW:\n"
        "- Shipping Manager checks the admin dashboard each morning for all orders in COMPLETED status.\n"
        "- These are paintings verified by the Owner and cleared for dispatch.\n"
        "\n"
        "STEP 1 — COURIER SELECTION:\n"
        "- Open the Shipping Dashboard and click 'Get Live Shipping Quotes' for each order.\n"
        "- Compare rates: India Post (Rs. 270), Delhivery Ground (Rs. 350), Delhivery Express (Rs. 472.50), DTDC (Rs. 585), Blue Dart Air (Rs. 715).\n"
        "- Select the courier based on: destination city, urgency, portrait size, and frame type.\n"
        "- For Gold Filigree 24x36 frames: always use Blue Dart Air.\n"
        "- Default recommendation: Delhivery Express for most metro orders.\n"
        "\n"
        "STEP 2 — PACKAGING:\n"
        "- Wrap painting in acid-free tissue, then bubble wrap (1-3 layers based on size).\n"
        "- Place in appropriately sized box with foam inserts or wooden brackets.\n"
        "- Add foam corner guards for framed paintings.\n"
        "\n"
        "STEP 3 — LABELING:\n"
        "- Print the shipping label using the 'Generate Label' button in the dashboard.\n"
        "- Attach tracking number sticker to the box exterior.\n"
        "- Mark the box: FRAGILE — DO NOT BEND on all 4 sides.\n"
        "\n"
        "STEP 4 — COURIER HANDOVER:\n"
        "- Hand the package to the courier pickup agent.\n"
        "- Confirm pickup acknowledgment from the courier.\n"
        "\n"
        "STEP 5 — SYSTEM UPDATE:\n"
        "- Update order status from COMPLETED to SHIPPED in the admin dashboard.\n"
        "- System automatically sends tracking number and courier name to the customer via email.\n"
        "- Customer can track using their tracking number on the order tracking page."
    ),

    # ─── ADMIN / BUSINESS KNOWLEDGE ───
    "business_strategy": (
        "WingsArtz Business Strategy & Analytics:\n"
        "- Primary Revenue: Custom portrait commissions (65% of revenue).\n"
        "- Secondary Revenue: Framing upsells and express delivery charges (35% of revenue).\n"
        "- Peak Season: October to January (Diwali, Christmas, New Year gift orders surge by 30-40%).\n"
        "- Top Markets: Chennai, Bengaluru, Mumbai, Hyderabad.\n"
        "- Target Customer: Middle to upper-middle class families ordering gift portraits.\n"
        "- Growth Levers: Instagram portfolio, referral discounts, festival promotions."
    ),

    "demand_forecasting": (
        "WingsArtz Demand Forecast Insights:\n"
        "- Diwali Season (Oct-Nov): 35-40% order surge expected. Pre-stock all canvas sizes by September.\n"
        "- Christmas/New Year (Dec-Jan): 25-30% surge. Focus on premium Gold Filigree frames.\n"
        "- Valentine's Day (Feb): 15-20% surge. Couples portraits, 8x10 and 11x14 most popular.\n"
        "- Summer (Apr-Jun): Slowest period. Good time for painter training and inventory audits.\n"
        "- Recommended Action: Maintain 150% of safety threshold stock levels 3 weeks before peak seasons."
    ),

    "kpi_explanation": (
        "WingsArtz KPI Definitions:\n"
        "- Total Revenue: Sum of all completed order values including delivery charges.\n"
        "- Average Order Value (AOV): Total Revenue divided by number of orders. Target: Rs. 12,000+.\n"
        "- Order Completion Rate: Percentage of accepted orders that reach SHIPPED status without cancellation.\n"
        "- Painter Utilization: Number of active jobs per painter vs. maximum capacity (usually 3 simultaneous).\n"
        "- Inventory Turnover: How fast materials are consumed vs. restocked. Target: < 2 weeks per restock cycle.\n"
        "- Customer Satisfaction: Based on delivery timeliness and repeat orders."
    ),
}


class RAGEngine:
    def __init__(self):
        self.is_mocked = (settings.OPENAI_API_KEY == "mock-key-for-development")

    def retrieve_context(self, query: str) -> list[str]:
        """
        Retrieves matching policy document chunks from the knowledge base.
        Uses keyword similarity for demo mode; ChromaDB embeddings when live API is configured.
        """
        query_lower = query.lower()

        if self.is_mocked:
            results = []

            # Priority keyword map - check broader topic keywords
            keyword_map = {
                "refund": "refunds",
                "cancel": "refunds",
                "money back": "refunds",
                "price": "pricing",
                "cost": "pricing",
                "rate": "pricing",
                "how much": "pricing",
                "charge": "pricing",
                "frame": "framing",
                "wood": "framing",
                "gold": "framing",
                "filigree": "framing",
                "shipping": "shipping_policy",
                "delivery": "shipping_policy",
                "deliver": "shipping_policy",
                "send": "shipping_policy",
                "ship": "shipping_policy",
                "courier": "courier_comparison",
                "delhivery": "courier_comparison",
                "blue dart": "courier_comparison",
                "dtdc": "courier_comparison",
                "india post": "courier_comparison",
                "speed post": "courier_comparison",
                "dispatch": "dispatch_workflow",
                "how much is shipping": "courier_comparison",
                "shipping rate": "courier_comparison",
                "shipping cost": "courier_comparison",
                "shipping price": "courier_comparison",
                "fastest shipping": "courier_comparison",
                "cheapest shipping": "courier_comparison",
                "track": "shipping_policy",
                "tracking": "shipping_policy",
                "express": "courier_comparison",
                "ground": "courier_comparison",
                "air": "courier_comparison",
                "chennai": "courier_comparison",
                "bengaluru": "courier_comparison",
                "hyderabad": "courier_comparison",
                "mumbai": "courier_comparison",
                "madurai": "courier_comparison",
                "coimbatore": "courier_comparison",
                "pack": "packaging_guide",
                "wrap": "packaging_guide",
                "bubble wrap": "packaging_guide",
                "box": "packaging_guide",
                "fragile": "packaging_guide",
                "day": "turnaround",
                "turnaround": "turnaround",
                "how long": "turnaround",
                "time": "turnaround",
                "dispatch": "dispatch_workflow",
                "fulfill": "dispatch_workflow",
                "workflow": "dispatch_workflow",
                "step by step": "dispatch_workflow",
                "how to ship": "dispatch_workflow",
                "durable": "durability",
                "clean": "durability",
                "care": "durability",
                "protect": "durability",
                "order": "order_process",
                "process": "order_process",
                "step": "order_process",
                "oil": "oil_technique",
                "acrylic": "acrylic_technique",
                "technique": "oil_technique",
                "canvas": "canvas_preparation",
                "priming": "canvas_preparation",
                "gesso": "canvas_preparation",
                "custom": "custom_instructions",
                "instruction": "custom_instructions",
                "portrait": "custom_instructions",
                "stock": "inventory_management",
                "inventory": "inventory_management",
                "restock": "inventory_management",
                "reorder": "inventory_management",
                "material": "material_properties",
                "linen": "material_properties",
                "paint set": "material_properties",
                "demand": "demand_forecasting",
                "forecast": "demand_forecasting",
                "diwali": "demand_forecasting",
                "season": "demand_forecasting",
                "festival": "demand_forecasting",
                "surge": "demand_forecasting",
                "kpi": "kpi_explanation",
                "revenue": "kpi_explanation",
                "aov": "kpi_explanation",
                "metric": "kpi_explanation",
                "strategy": "business_strategy",
                "business": "business_strategy",
                "market": "business_strategy",
                "growth": "business_strategy",
            }

            matched_keys = set()
            for keyword, kb_key in keyword_map.items():
                if keyword in query_lower and kb_key not in matched_keys:
                    results.append(KNOWLEDGE_BASE[kb_key])
                    matched_keys.add(kb_key)

            # Fallback if nothing matched
            if not results:
                results.append(
                    "WingsArtz General Information: We create custom hand-painted portraits on premium cotton and linen canvases. "
                    "Prices start from Rs. 6,000 for 8x10 inch portraits. Orders take 7 to 10 working days to complete. "
                    "We ship across India using Delhivery, Blue Dart, DTDC, and India Post."
                )
            return results

        else:
            try:
                import chromadb
                client = chromadb.PersistentClient(path="backend/static/chroma_db")
                collection = client.get_or_create_collection("wingsartz_policies")

                # Seed collection if empty
                if collection.count() == 0:
                    for doc_id, text in KNOWLEDGE_BASE.items():
                        collection.add(
                            documents=[text],
                            ids=[doc_id],
                            metadatas=[{"category": doc_id}]
                        )

                query_results = collection.query(
                    query_texts=[query],
                    n_results=3
                )

                flat_list = []
                if query_results and 'documents' in query_results:
                    for doc_group in query_results['documents']:
                        flat_list.extend(doc_group)
                return flat_list

            except Exception as e:
                print(f"ChromaDB retrieval failed: {e}. Falling back to keyword search.")
                return [KNOWLEDGE_BASE["refunds"]]


rag_engine = RAGEngine()
