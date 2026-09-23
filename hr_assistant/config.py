"""All settings for the app live here, in one place."""


import os 
from dotenv import load_dotenv

load_dotenv(override=True)

def _clean_env(key: str, default: str | None = None) -> str | None:
    """Retrieve environment variable and strip surrounding quotes/whitespace.
    Bridges Streamlit secrets into os.environ for cloud deployment."""
    val = os.getenv(key)
    if not val:
        try:
            import streamlit as st
            if hasattr(st, "secrets"):
                if key in st.secrets:
                    val = str(st.secrets[key])
                elif key.lower() in st.secrets:
                    val = str(st.secrets[key.lower()])
                elif key.upper() in st.secrets:
                    val = str(st.secrets[key.upper()])
        except Exception:
            pass

    if val is not None:
        val = val.strip()
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1].strip()
        os.environ[key] = val
        return val

    return default

## ENV VAR / SECRET - LLMS 

GROQ_API_KEY = _clean_env("GROQ_API_KEY")
JINA_API_KEY = _clean_env("JINA_API_KEY")

# GATEWAY 

PORTKEY_API_KEY = _clean_env("PORTKEY_API_KEY")

# GUARD MODEL 

GUARD_MODEL_NAME = _clean_env("GUARD_MODEL_NAME", "openai/gpt-oss-safeguard-20b")

# TRACING 

LANGSMITH_TRACING = _clean_env("LANGSMITH_TRACING", "false")
LANGSMITH_ENDPOINT = _clean_env("LANGSMITH_ENDPOINT")
LANGSMITH_API_KEY = _clean_env("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = _clean_env("LANGSMITH_PROJECT")





## DEFINE PATH - DATA / VECTOR STORE 

DATA_FILE_PATH = os.path.join("data", "hr_policy.txt")

## VECTORE STORES 

# IN MEMORY 
# persistent memory - vectors # 100gb - ingestion 
# cloud memory 

QDRANT_URL = _clean_env("QDRANT_URL")
QDRANT_API_KEY = _clean_env("QDRANT_API_KEY")
QDRANT_COLLECTION_NAME = _clean_env("QDRANT_COLLECTION_NAME", "hr-assistant")

## MODELS 
# LLM and EMBEDING MODEL 

VALID_GROQ_MODELS = {"openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b", "allam-2-7b"}

raw_llm_model = _clean_env("LLM_MODEL_NAME", "openai/gpt-oss-120b")
if not raw_llm_model or raw_llm_model.lower() not in VALID_GROQ_MODELS:
    LLM_MODEL_NAME = "openai/gpt-oss-120b"
else:
    LLM_MODEL_NAME = raw_llm_model

EMBEDDING_MODEL_NAME = "jina-embeddings-v2-base-en"

## CHUNK / TEXT SPLITTING CONFIG 

CHUNK_SIZE = 500
CHUNK_OVERLAP = 60

# RETRIVAL RESULTS 
TOP_K_RESULTS = 3


## SYSTEM INSTRUCTIONS 

SYSTEM_PROMPT = (
    "You are a friendly HR assistant. Always use the search_hr_policy tool to look up "
    "facts before answering. If the answer isn't in the search results, say you don't know "
    "instead of guessing."
)


def check_api_keys() -> None:
    """Stop early with a clear message if a required API key is missing."""
    if not GROQ_API_KEY:
        raise ValueError("Missing GROQ_API_KEY. Please add it to your .env file or Streamlit Cloud Secrets.")
    if not JINA_API_KEY:
        raise ValueError("Missing JINA_API_KEY. Please add it to your .env file or Streamlit Cloud Secrets.")
    if not QDRANT_URL or not QDRANT_API_KEY:
        raise ValueError("Missing QDRANT_URL/QDRANT_API_KEY. Please add them to your .env file or Streamlit Cloud Secrets.")
    if not PORTKEY_API_KEY:
        raise ValueError("Missing PORTKEY_API_KEY. Please add it to your .env file or Streamlit Cloud Secrets.")


# Legacy / Compatibility Aliases
EMBEDDING_MODEL = EMBEDDING_MODEL_NAME
GROQ_MODEL = LLM_MODEL_NAME

# Setup LangChain / LangSmith Tracing Environment Variables
if LANGSMITH_TRACING and LANGSMITH_TRACING.lower() == "true":
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    if LANGSMITH_ENDPOINT:
        os.environ["LANGCHAIN_ENDPOINT"] = LANGSMITH_ENDPOINT
    if LANGSMITH_API_KEY:
        os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    if LANGSMITH_PROJECT:
        os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT