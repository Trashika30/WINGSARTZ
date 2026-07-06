# WingsArtz Hybrid AI ERP System

WingsArtz is an intelligent, AI-driven ERP and storefront designed specifically for custom portrait studios. It replaces traditional rigid dashboards with a conversational, context-aware AI assistant powered by a Hybrid LLM + RAG architecture.

## 🚀 Deployment (Vercel)
This project is configured for one-click deployment on **Vercel** using `@vercel/python`.
1. Push this repository to GitHub.
2. Import the repository into Vercel.
3. Vercel will automatically read `vercel.json` and `requirements.txt` to deploy the FastAPI backend and serve the static frontend.
*(Note: SQLite acts as a read-only database in Vercel's serverless environment).*

---

## 🧠 Hybrid AI Orchestration Workflow

The core of the WingsArtz intelligence lies in `backend/app/ai/hybrid_agent.py`. Rather than relying on a single data source, the agent orchestrates multiple streams of data before reasoning.

### Workflow Pipeline
1. **User Query Input:** The user asks a question in the chat interface.
2. **Conversation Memory Retrieval:** The agent fetches the last 6 messages of the session to maintain multi-turn conversational context.
3. **Intent Detection:** An initial LLM classification (or regex fallback) evaluates the query to determine the required tools:
   - `DATABASE` (Order numbers, stock levels, assignments)
   - `RAG_POLICY` (Return policies, drying techniques, canvas prep)
   - `TOOL_SHIPPING` / `TOOL_WEATHER` (External API dependencies)
   - `STRATEGY` (High-level business consulting)
4. **Context Gathering:** Based on the detected intent, the system triggers the necessary tools:
   - Queries the SQLite database via SQLAlchemy.
   - Queries the RAG knowledge base for text chunks.
   - Pings mocked external APIs.
5. **Synthesis & Generation:** The gathered context is bundled into a massive system prompt and sent to the LLM (Gemini or Groq). The LLM acts as the reasoning engine to generate a natural, conversational, and strategic response.

## Tech Stack
- **Backend:** Python, FastAPI, SQLAlchemy (SQLite)
- **Frontend:** Vanilla HTML/CSS/JS, Marked.js
- **AI Models:** Google Gemini 2.5 Flash (Primary), Groq Llama 3.1 8B (Fallback)
