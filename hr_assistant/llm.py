import requests
from typing import List, Dict, Any
from hr_assistant.config import GROQ_API_KEY, GROQ_MODEL, PORTKEY_API_KEY
from portkey_ai import createHeaders, PORTKEY_GATEWAY_URL


class GroqLLM:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or GROQ_API_KEY
        raw_model = model or GROQ_MODEL
        if raw_model and "qwen" in str(raw_model).lower():
            self.model = "llama-3.3-70b-versatile"
        else:
            self.model = raw_model
        self.api_url = f"{PORTKEY_GATEWAY_URL}/chat/completions" if PORTKEY_API_KEY else "https://api.groq.com/openai/v1/chat/completions"

    def invoke(self, messages: List[Dict[str, str]]) -> str:
        if PORTKEY_API_KEY:
            headers = createHeaders(api_key=PORTKEY_API_KEY, provider="@hrpolicy")
            headers["Content-Type"] = "application/json"
        else:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

        valid_models = ["llama-3.3-70b-versatile", "llama3-70b-8192", "llama3-8b-8192", "gemma2-9b-it"]
        models_to_try = [self.model] + valid_models
        models_to_try = list(dict.fromkeys([m for m in models_to_try if m and "qwen" not in m.lower() and "compound" not in m.lower()]))
        if not models_to_try:
            models_to_try = valid_models

        last_error = ""

        # 1. Try Portkey Gateway with direct groq provider (passes active Groq model directly)
        if PORTKEY_API_KEY:
            try:
                pk_groq_headers = createHeaders(api_key=PORTKEY_API_KEY, provider="groq")
                pk_groq_headers["Content-Type"] = "application/json"
                for m in models_to_try:
                    payload = {"model": m, "messages": messages, "temperature": 0.2}
                    resp = requests.post(self.api_url, json=payload, headers=pk_groq_headers, timeout=45)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        last_error = f"Portkey Groq Status {resp.status_code}: {resp.text}"
            except Exception as e:
                last_error = str(e)

        # 2. Try Portkey Gateway with @hrpolicy provider
        if PORTKEY_API_KEY:
            try:
                headers = createHeaders(api_key=PORTKEY_API_KEY, provider="@hrpolicy")
                headers["Content-Type"] = "application/json"
                for m in models_to_try:
                    payload = {"model": m, "messages": messages, "temperature": 0.2}
                    resp = requests.post(self.api_url, json=payload, headers=headers, timeout=45)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
            except Exception:
                pass

        # 3. Direct Groq API failover
        groq_key = self.api_key or GROQ_API_KEY
        if groq_key:
            groq_url = "https://api.groq.com/openai/v1/chat/completions"
            groq_headers = {
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            }
            for m in valid_models:
                payload = {"model": m, "messages": messages, "temperature": 0.2}
                try:
                    resp = requests.post(groq_url, json=payload, headers=groq_headers, timeout=45)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        last_error = f"Direct Groq Status {resp.status_code}: {resp.text}"
                except Exception as e:
                    last_error = str(e)

        return f"[API Error]: Failed to generate response ({last_error})"


def get_llm() -> GroqLLM:
    """Returns dynamic Groq LLM instance."""
    return GroqLLM()

