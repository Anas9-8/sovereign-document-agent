"""Ollama LLM calls for answer generation."""

import os
import time

from langchain_ollama import OllamaLLM

from src.logger import get_logger

logger = get_logger(__name__)

PROMPT_TEMPLATE = """You are a precise assistant. Answer only based on the provided context. If the answer is not in the context, say so.

Context:
{context}

Question: {question}
Answer:"""


def _get_llm():
    """Return a configured Ollama LLM instance."""
    return OllamaLLM(
        model=os.getenv("OLLAMA_MODEL", "llama3"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )


def _build_prompt(question, context_chunks):
    """Format the prompt template with context and question."""
    context = "\n\n".join(chunk["text"] for chunk in context_chunks)
    return PROMPT_TEMPLATE.format(context=context, question=question)


def generate_answer(question, context_chunks):
    """Send question + context to Ollama and return the answer with latency."""
    prompt = _build_prompt(question, context_chunks)
    llm = _get_llm()

    start = time.time()
    answer = llm.invoke(prompt)
    latency_ms = int((time.time() - start) * 1000)

    logger.info("Generated answer in %dms", latency_ms)
    return {"answer": answer.strip(), "latency_ms": latency_ms}
