"""Step 4: store chunk embeddings in Qdrant Cloud so we can search them later."""


from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from hr_assistant import config
from hr_assistant.embeddings import get_embeddings_model
from hr_assistant.logger import get_logger

logger = get_logger(__name__)


# build_vector_store

def build_vector_store(chunks):
    """Embed every chunk and upload it into a Qdrant Cloud collection.
    Falls back to an in-memory Qdrant store if cloud is unreachable."""
    logger.info(
        "Embedding %d chunk(s) and uploading to Qdrant collection '%s'...",
        len(chunks),
        config.QDRANT_COLLECTION_NAME,
    )
    embeddings_model = get_embeddings_model()
    if config.QDRANT_URL and config.QDRANT_API_KEY:
        try:
            vector_store = QdrantVectorStore.from_documents(
                chunks,
                embedding=embeddings_model,
                url=config.QDRANT_URL,
                api_key=config.QDRANT_API_KEY,
                collection_name=config.QDRANT_COLLECTION_NAME,
            )
            logger.info("Uploaded to Qdrant collection '%s'", config.QDRANT_COLLECTION_NAME)
            return vector_store
        except Exception as e:
            logger.warning(
                "Failed to connect/upload to Qdrant Cloud collection (%s). Falling back to in-memory vector store.", e
            )

    logger.info("Building in-memory Qdrant vector store fallback...")
    return QdrantVectorStore.from_documents(
        chunks,
        embedding=embeddings_model,
        location=":memory:",
        collection_name=config.QDRANT_COLLECTION_NAME,
    )


def load_vector_store():
    """Connect to a Qdrant Cloud collection that was already built before."""
    logger.info("Connecting to existing Qdrant collection '%s'", config.QDRANT_COLLECTION_NAME)
    embeddings_model = get_embeddings_model()
    try:
        return QdrantVectorStore.from_existing_collection(
            embedding=embeddings_model,
            url=config.QDRANT_URL,
            api_key=config.QDRANT_API_KEY,
            collection_name=config.QDRANT_COLLECTION_NAME,
        )
    except Exception as e:
        logger.warning(
            "Failed to load existing Qdrant Cloud collection (%s). Will recreate vector store.", e
        )
        return None


def vector_store_exists() -> bool:
    """Check if the Qdrant Cloud collection already exists safely."""
    if not config.QDRANT_URL or not config.QDRANT_API_KEY:
        return False
    try:
        client = QdrantClient(
            url=config.QDRANT_URL,
            api_key=config.QDRANT_API_KEY,
            timeout=5,
        )
        return client.collection_exists(config.QDRANT_COLLECTION_NAME)
    except Exception as e:
        logger.warning("Could not reach Qdrant Cloud collection (Error: %s).", e)
        return False


def get_retriever(vector_store, k: int = config.TOP_K_RESULTS):
    """Turn a vector store into a retriever
    that returns the top-k matching chunks."""
    logger.info("Creating retriever with top_k=%d", k)
    return vector_store.as_retriever(search_kwargs={"k": k})
