"""
WingsArtz LLM Provider
======================
Priority cascade:
  1. Google Gemini (primary)     — gemini-1.5-flash
  2. Groq                        — llama3-8b-8192  (fallback if Gemini fails/expired)
  3. OpenAI                      — gpt-3.5-turbo   (last resort)
  4. Smart keyword rules         — built-in offline fallback (no API needed)

Usage:
    from backend.app.ai.llm_provider import call_llm

    response = call_llm(system_prompt, user_query)
    if response is None:
        # use keyword fallback rules
"""

import os
from backend.app.core.config import settings


def call_llm(system_prompt: str, user_query: str, temperature: float = 0.3) -> str | None:
    """
    Try LLMs in priority order: Gemini → Groq → OpenAI.
    Returns the response text, or None if all providers fail
    (caller should then use keyword-based fallback rules).
    """

    # ── 1. GOOGLE GEMINI (Primary) ─────────────────────────────────────────────
    if settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=system_prompt
            )
            response = model.generate_content(
                user_query,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=350,
                )
            )
            text = response.text.strip()
            if text:
                print("[LLM] Gemini responded successfully.")
                return text
        except Exception as e:
            err = str(e)
            if "API_KEY_INVALID" in err or "PERMISSION_DENIED" in err or "expired" in err.lower() or "invalid" in err.lower():
                print(f"[LLM] Gemini key invalid/expired: {err}. Trying Groq...")
            else:
                print(f"[LLM] Gemini error: {err}. Trying Groq...")

    # ── 2. GROQ (Fallback 1) ───────────────────────────────────────────────────
    if settings.GROQ_API_KEY:
        try:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY)
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=temperature,
                max_tokens=350,
            )
            text = completion.choices[0].message.content.strip()
            if text:
                print("[LLM] Groq (llama3-70b) responded successfully.")
                return text
        except Exception as e:
            print(f"[LLM] Groq error: {e}. Trying OpenAI...")

    # ── 3. OPENAI (Fallback 2) ─────────────────────────────────────────────────
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "mock-key-for-development":
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            res = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=temperature,
                max_tokens=350,
            )
            text = res.choices[0].message.content.strip()
            if text:
                print("[LLM] OpenAI GPT-3.5 responded successfully.")
                return text
        except Exception as e:
            print(f"[LLM] OpenAI error: {e}. All LLM providers failed.")

    # ── 4. All providers failed → caller uses keyword rules ────────────────────
    print("[LLM] All LLM providers unavailable. Using smart keyword rules.")
    return None


def get_active_provider() -> str:
    """Returns the name of the first available LLM provider (for status display)."""
    if settings.GEMINI_API_KEY:
        return "Google Gemini 1.5 Flash"
    if settings.GROQ_API_KEY:
        return "Groq (Llama3-70b)"
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "mock-key-for-development":
        return "OpenAI GPT-3.5"
    return "Smart Keyword Rules (Offline)"
