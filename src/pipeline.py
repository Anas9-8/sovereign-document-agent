"""Connects retriever to generator for end-to-end RAG queries."""

import os
import time

from src.retriever import get_relevant_chunks
from src.generator import generate_answer
from src.logger import get_logger

logger = get_logger(__name__)


def run_query(question, top_k=None):
    """Retrieve context and generate an answer for the given question."""
    if top_k is None:
        top_k = int(os.getenv("TOP_K_RESULTS", "3"))

    start = time.time()

    chunks = get_relevant_chunks(question, top_k=top_k)
    sources = list({chunk["source"] for chunk in chunks})
    result = generate_answer(question, chunks)

    total_ms = int((time.time() - start) * 1000)

    logger.info("Pipeline: '%s...' — %dms total", question[:60], total_ms)
    return {
        "answer": result["answer"],
        "sources": sources,
        "latency_ms": total_ms,
        "chunks_used": len(chunks),
    }
