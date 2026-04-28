import os
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import BaseModel

from src.ingestor import ingest_file
from src.pipeline import run_query
from src import registry

router = APIRouter()

DOCS_PATH = Path(os.getenv("DOCS_PATH", "./data/docs"))


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


class UploadResponse(BaseModel):
    status: str
    filename: str
    chunks_created: int
    message: str | None = None


@router.post("/ingest", response_model=IngestResponse)
def ingest_document(req: IngestRequest):
    return ingest_file(req.file_path)


@router.post("/query", response_model=QueryResponse)
def query_documents(req: QueryRequest):
    return run_query(req.question, top_k=req.top_k)


@router.get("/documents", response_model=DocumentsResponse)
def list_documents():
    docs = registry.get_all()
    return {"documents": docs, "total": len(docs)}


@router.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "ok",
        "indexed_docs": registry.count(),
        "model": os.getenv("OLLAMA_MODEL", "llama3.2:1b"),
    }


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    force: bool = Query(False, description="Force re-ingest even if already indexed"),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in {".pdf", ".docx", ".txt", ".csv"}:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Supported: .pdf, .docx, .txt, .csv",
        )

    DOCS_PATH.mkdir(parents=True, exist_ok=True)

    file_path = DOCS_PATH / file.filename

    content = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    result = ingest_file(str(file_path), force=force)

    if result["status"] == "skipped":
        return {
            "status": "skipped",
            "filename": file.filename,
            "chunks_created": 0,
            "message": "File already indexed. Use force=true to re-ingest.",
        }

    if result["status"].startswith("invalid"):
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=result["status"])

    if result["status"] == "ok":
        return {
            "status": "success",
            "filename": file.filename,
            "chunks_created": result["chunks_created"],
            "message": f"Successfully ingested {result['chunks_created']} chunks",
        }

    return {
        "status": result["status"],
        "filename": file.filename,
        "chunks_created": result["chunks_created"],
        "message": None,
    }
