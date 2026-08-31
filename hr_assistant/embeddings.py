from typing import List
import requests
from langchain_core.embeddings import Embeddings
from hr_assistant.config import JINA_API_KEY, EMBEDDING_MODEL


class JinaEmbeddings(Embeddings):
    API_URL = "https://api.jina.ai/v1/embeddings"

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or JINA_API_KEY
        self.model = model or EMBEDDING_MODEL

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {"model": self.model, "input": texts}
        resp = requests.post(self.API_URL, json=payload, headers=headers, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"Jina API Error ({resp.status_code}): {resp.text}")
        data = resp.json()
        sorted_data = sorted(data.get("data", []), key=lambda x: x.get("index", 0))
        return [item["embedding"] for item in sorted_data]

    def embed_query(self, text: str) -> List[float]:
        embeddings = self.embed_documents([text])
        return embeddings[0] if embeddings else []


def get_embeddings() -> JinaEmbeddings:
    """Returns dynamic embedding model instance."""
    return JinaEmbeddings()


def get_embeddings_model() -> JinaEmbeddings:
    """Returns dynamic embedding model instance."""
    return JinaEmbeddings()

