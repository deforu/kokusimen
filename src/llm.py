import os
from typing import Optional

import google.generativeai as genai


def setup_gemini(api_key: Optional[str] = None, model_name: Optional[str] = None):
    if api_key is None:
        # Prefer GEMINI_API_KEY; fallback to GOOGLE_API_KEY for compatibility
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY が未設定です。環境変数 GEMINI_API_KEY（または GOOGLE_API_KEY）を設定してください。"
        )

    genai.configure(api_key=api_key)
    if model_name is None:
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    return genai.GenerativeModel(model_name)


def ask_gemini(model, user_text: str, system_prompt: Optional[str] = None) -> str:
    prompt = (
        user_text if not system_prompt else f"{system_prompt}\n\nユーザー: {user_text}"
    )
    resp = model.generate_content(prompt)
    return getattr(resp, "text", "") or ""
