import requests
from typing import List, Dict, Any
from hr_assistant.config import GROQ_API_KEY, GROQ_MODEL, PORTKEY_API_KEY
from portkey_ai import createHeaders, PORTKEY_GATEWAY_URL


VALID_GROQ_MODELS = {"openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b", "allam-2-7b"}


class GroqLLM:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or GROQ_API_KEY
        raw_model = model or GROQ_MODEL
        if not raw_model or str(raw_model).lower() not in VALID_GROQ_MODELS:
            self.model = "openai/gpt-oss-120b"
        else:
            self.model = raw_model
        self.api_url = f"{PORTKEY_GATEWAY_URL}/chat/completions" if PORTKEY_API_KEY else "https://api.groq.com/openai/v1/chat/completions"

    def invoke(self, messages: List[Dict[str, str]]) -> str:
        if PORTKEY_API_KEY:
            headers = createHeaders(api_key=PORTKEY_API_KEY, provider="@HRPOLICY")
            headers["Content-Type"] = "application/json"
        else:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

        models_to_try = [
            self.model,
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3.8-27b"
        ]
        models_to_try = list(dict.fromkeys([m for m in models_to_try if m and str(m).lower() in VALID_GROQ_MODELS]))
        if not models_to_try:
            models_to_try = ["openai/gpt-oss-120b"]

        last_error = ""

        # 1. Direct Groq API
        groq_key = self.api_key or GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        if groq_key:
            groq_url = "https://api.groq.com/openai/v1/chat/completions"
            groq_headers = {
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            }
            for m in models_to_try:
                payload = {"model": m, "messages": messages, "temperature": 0.2}
                try:
                    resp = requests.post(groq_url, json=payload, headers=groq_headers, timeout=30)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        last_error = f"Direct Groq model '{m}' Status {resp.status_code}: {resp.text}"
                except Exception as e:
                    last_error = str(e)

        # 2. Portkey Gateway fallback (with saved integration slug @HRPOLICY)
        pk_key = PORTKEY_API_KEY or os.getenv("PORTKEY_API_KEY")
        if pk_key:
            try:
                headers = createHeaders(api_key=pk_key, provider="@HRPOLICY")
                headers["Content-Type"] = "application/json"
                for m in models_to_try:
                    payload = {"model": m, "messages": messages, "temperature": 0.2}
                    resp = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        last_error = f"Portkey model '{m}' Status {resp.status_code}: {resp.text}"
            except Exception as e:
                last_error = str(e)

        return f"[API Error]: Failed to generate response ({last_error})"


def get_llm() -> GroqLLM:
    """Returns dynamic Groq LLM instance."""
    return GroqLLM()

