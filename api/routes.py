"""All API endpoints."""

import os

from fastapi import APIRouter
from pydantic import BaseModel

from src.ingestor import ingest_file
from src.pipeline import run_query
from src import registry

router = APIRouter()


class IngestRequest(BaseModel):
    file_path: str


class IngestResponse(BaseModel):
    status: str
    doc_name: str
    chunks_created: int


class QueryRequest(BaseModel):
    question: str
    top_k: int = 3


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    latency_ms: int


class DocumentsResponse(BaseModel):
    documents: list[dict]
    total: int


class HealthResponse(BaseModel):
    status: str
    indexed_docs: int
    model: str


@router.post("/ingest", response_model=IngestResponse)
def ingest_document(req: IngestRequest):
    """Ingest a document into the vector store."""
    result = ingest_file(req.file_path)
    return result


@router.post("/query", response_model=QueryResponse)
def query_documents(req: QueryRequest):
    """Query the RAG pipeline with a question."""
    result = run_query(req.question, top_k=req.top_k)
    return result


@router.get("/documents", response_model=DocumentsResponse)
def list_documents():
    """List all indexed documents."""
    docs = registry.get_all()
    return {"documents": docs, "total": len(docs)}


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check."""
    return {
        "status": "ok",
        "indexed_docs": registry.count(),
        "model": os.getenv("OLLAMA_MODEL", "llama3"),
    }
