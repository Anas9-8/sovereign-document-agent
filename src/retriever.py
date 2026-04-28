import os

from src.vectorstore import get_vectorstore
from src.logger import get_logger

logger = get_logger(__name__)


def get_relevant_chunks(question, top_k=None):
    if top_k is None:
        top_k = int(os.getenv("TOP_K_RESULTS", "5"))

    vs = get_vectorstore()
    results = vs.similarity_search_with_relevance_scores(question, k=top_k)

    logger.info("Retrieved %d chunks for query: '%s...'", len(results), question[:50])

    chunks = [
        {
            "text": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "score": round(score, 4),
        }
        for doc, score in results
    ]

    for chunk in chunks:
        logger.debug("  - %s (score: %.4f)", chunk["source"], chunk["score"])

    return chunks


def get_collection_size():
    return get_vectorstore()._collection.count()
