import os
import threading

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from src.logger import get_logger

logger = get_logger(__name__)

_vectorstore_instance = None
_vectorstore_lock = threading.Lock()


def get_vectorstore():
    global _vectorstore_instance
    if _vectorstore_instance is None:
        with _vectorstore_lock:
            if _vectorstore_instance is None:
                embeddings = OllamaEmbeddings(
                    model=os.getenv("OLLAMA_MODEL", "llama3.2:1b"),
                    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                )
                _vectorstore_instance = Chroma(
                    collection_name="documents",
                    persist_directory=os.getenv("CHROMA_PATH", "./data/chroma"),
                    embedding_function=embeddings,
                )
                logger.info("Initialized ChromaDB vectorstore")
    return _vectorstore_instance


def persist_vectorstore():
    if _vectorstore_instance is not None:
        with _vectorstore_lock:
            if hasattr(_vectorstore_instance, "persist"):
                _vectorstore_instance.persist()
            logger.info("Persisted ChromaDB to disk")


def clear_vectorstore():
    global _vectorstore_instance
    with _vectorstore_lock:
        if _vectorstore_instance is not None:
            _vectorstore_instance.delete_collection()
            _vectorstore_instance = None
            logger.info("Cleared ChromaDB collection")
