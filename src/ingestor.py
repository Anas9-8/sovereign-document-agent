"""Document loading, chunking, embedding, and storage."""

import os
import time
from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from src.logger import get_logger
from src.validator import validate_file
from src import registry

logger = get_logger(__name__)


def _get_vectorstore():
    """Return the persistent ChromaDB vectorstore."""
    chroma_path = os.getenv("CHROMA_PATH", "./data/chroma")
    embeddings = OllamaEmbeddings(
        model=os.getenv("OLLAMA_MODEL", "llama3"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )
    return Chroma(
        collection_name="documents",
        persist_directory=chroma_path,
        embedding_function=embeddings,
    )


def load_document(file_path):
    """Load a file and return its raw text."""
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        reader = PdfReader(file_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif ext == ".docx":
        doc = DocxDocument(file_path)
        text = "\n".join(p.text for p in doc.paragraphs)
    elif ext in (".txt", ".csv"):
        text = path.read_text(encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    logger.info("Loaded: %s (%d chars)", path.name, len(text))
    return text


def chunk_text(text):
    """Split text into chunks using LangChain splitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=int(os.getenv("CHUNK_SIZE", "500")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50")),
    )
    chunks = splitter.split_text(text)
    logger.info("Chunked into %d pieces", len(chunks))
    return chunks


def _store_chunks(chunks, source_name):
    """Embed and store chunks in ChromaDB."""
    vectorstore = _get_vectorstore()
    metadatas = [{"source": source_name}] * len(chunks)
    ids = [f"{source_name}_{i}" for i in range(len(chunks))]
    vectorstore.add_texts(texts=chunks, metadatas=metadatas, ids=ids)
    logger.info("Stored %d chunks for %s", len(chunks), source_name)


def ingest_file(file_path, force=False):
    """Validate, load, chunk, embed, store, and register a document."""
    path = Path(file_path)

    if not force and registry.is_indexed(path.name):
        logger.info("Skipped (already indexed): %s", path.name)
        return {"doc_name": path.name, "chunks_created": 0, "status": "skipped"}

    valid, reason = validate_file(file_path)
    if not valid:
        logger.warning("Invalid file: %s — %s", path.name, reason)
        return {"doc_name": path.name, "chunks_created": 0, "status": f"invalid: {reason}"}

    start = time.time()
    text = load_document(file_path)
    chunks = chunk_text(text)
    _store_chunks(chunks, path.name)
    registry.add_entry(path.name, len(chunks))
    elapsed = int((time.time() - start) * 1000)

    logger.info("Ingested: %s — %d chunks in %dms", path.name, len(chunks), elapsed)
    return {"doc_name": path.name, "chunks_created": len(chunks), "status": "ok"}


def ingest_folder(folder_path=None):
    """Ingest all supported files in a folder."""
    folder = Path(folder_path or os.getenv("DOCS_PATH", "./data/docs"))
    supported = {".pdf", ".txt", ".docx", ".csv"}

    files = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in supported]
    logger.info("Found %d supported files in %s", len(files), folder)

    return [ingest_file(str(f)) for f in sorted(files)]
