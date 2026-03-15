"""ChromaDB queries for relevant document chunks."""

import os

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from src.logger import get_logger

logger = get_logger(__name__)


def _get_vectorstore():
    """Return the persistent ChromaDB vectorstore."""
    embeddings = OllamaEmbeddings(
        model=os.getenv("OLLAMA_MODEL", "llama3"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )
    return Chroma(
        collection_name="documents",
        persist_directory=os.getenv("CHROMA_PATH", "./data/chroma"),
        embedding_function=embeddings,
    )


def get_relevant_chunks(question, top_k=None):
    """Query ChromaDB for chunks most similar to the question."""
    if top_k is None:
        top_k = int(os.getenv("TOP_K_RESULTS", "3"))

    vectorstore = _get_vectorstore()
    results = vectorstore.similarity_search_with_relevance_scores(question, k=top_k)

    chunks = [
        {
            "text": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "score": round(score, 4),
        }
        for doc, score in results
    ]

    logger.info("Query: '%s...' — %d chunks found", question[:60], len(chunks))
    return chunks


def get_collection_size():
    """Return total number of chunks stored in ChromaDB."""
    vectorstore = _get_vectorstore()
    collection = vectorstore._collection
    return collection.count()
