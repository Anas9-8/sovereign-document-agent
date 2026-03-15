import os
import time

from langchain_ollama import OllamaLLM

from src.logger import get_logger

logger = get_logger(__name__)

PROMPT = """Answer only based on the context below. If the answer is not there, say so.

Context:
{context}

Question: {question}
Answer:"""


def _get_llm():
    return OllamaLLM(
        model=os.getenv("OLLAMA_MODEL", "llama3"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )


def generate_answer(question, context_chunks):
    context = "\n\n".join(chunk["text"] for chunk in context_chunks)
    prompt = PROMPT.format(context=context, question=question)

    start = time.time()
    answer = _get_llm().invoke(prompt)
    latency_ms = int((time.time() - start) * 1000)

    logger.info("Generated answer in %dms", latency_ms)
    return {"answer": answer.strip(), "latency_ms": latency_ms}
