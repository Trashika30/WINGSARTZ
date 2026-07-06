# WingsArtz API & Chatbot Test Cases

This document outlines 10 critical test cases to verify the Hybrid LLM + RAG architecture and FastAPI backend.

## Test Cases

| Test ID | Category | Description | Execution Steps | Expected Result |
|---|---|---|---|---|
| **TC-01** | Authentication | Owner Login Verification | 1. Navigate to `/app/admin.html`<br>2. Login with `owner@wingsartz.com` / `WingsOwner2026!` | Login successful, dashboard renders, and Active Role is identified as "Owner". |
| **TC-02** | Authentication | Painter Login Verification | 1. Navigate to `/app/admin.html`<br>2. Login with `painter1@wingsartz.com` / `WingsPainter2026!` | Login successful, financial KPIs are hidden, only assigned jobs are visible. |
| **TC-03** | AI Agent | Intent Detection: Database | 1. Login as Owner.<br>2. Ask chatbot: "How many pending orders do we have?" | Agent correctly queries live DB and responds with accurate order numbers instead of RAG policy data. |
| **TC-04** | AI Agent | Intent Detection: RAG Policy | 1. Ask chatbot: "What is the return policy for custom portraits?" | Agent queries local knowledge base (RAG) and accurately outputs the 14-day policy. |
| **TC-05** | AI Agent | Conversation Memory | 1. Ask chatbot: "How many active orders?"<br>2. Follow up: "Which of those are delayed?" | Agent understands "those" refers to the active orders mentioned in the previous turn. |
| **TC-06** | AI Agent | External Tool: Shipping API | 1. Ask chatbot: "What are the current delivery rates via Blue Dart?" | Agent correctly maps intent to `TOOL_SHIPPING` and returns the live/mocked Blue Dart API rate (Rs. 700). |
| **TC-07** | AI Agent | External Tool: Weather API | 1. Ask chatbot: "How is the weather affecting oil paint drying times?" | Agent routes to `TOOL_WEATHER` and advises on the 24-hour extension due to humidity. |
| **TC-08** | AI Agent | Role-Based Access Control (Chat) | 1. Login as Painter.<br>2. Ask chatbot: "What was our total revenue last month?" | Chatbot API immediately blocks the query (403 Forbidden) and refuses to fetch financial data for painters. |
| **TC-09** | System | Fallback Provider Failover | 1. Provide an invalid Gemini API key.<br>2. Ask a question. | System seamlessly falls back to Groq (Llama 3.1) and successfully generates a response without crashing. |
| **TC-10** | Database | Reorder Threshold Alert | 1. Submit a query asking for "low stock items". | Agent accurately identifies which inventory items are below the `safety_threshold` and suggests reorder quantities. |
