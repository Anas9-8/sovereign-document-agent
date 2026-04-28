import os
import time

from langchain_ollama import OllamaLLM

from src.logger import get_logger

logger = get_logger(__name__)

PROMPT = """Answer based on the context below. Cite the source filename in your answer.

Context:
{context}

Question: {question}

Answer:"""


_llm_instance = None


def _get_llm():
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = OllamaLLM(
            model=os.getenv("OLLAMA_MODEL", "llama3.2:1b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
    return _llm_instance


def generate_answer(question, context_chunks):
    if not context_chunks:
        return {
            "answer": "I don't have any relevant information to answer this question.",
            "latency_ms": 0,
        }

    sources = list({chunk.get("source", "unknown") for chunk in context_chunks})

    context_parts = []
    for i, chunk in enumerate(context_chunks[:5], 1):
        source = chunk.get("source", "unknown")
        text = chunk.get("text", "")
        context_parts.append(f"[{source}]\n{text}")

    context = "\n\n---\n\n".join(context_parts)
    prompt = PROMPT.format(context=context, question=question)

    start = time.time()
    answer = _get_llm().invoke(prompt)
    latency_ms = int((time.time() - start) * 1000)

    logger.info(
        "Generated answer in %dms using %d chunks from %d sources",
        latency_ms,
        len(context_chunks[:5]),
        len(sources),
    )

    return {"answer": answer.strip(), "latency_ms": latency_ms}
