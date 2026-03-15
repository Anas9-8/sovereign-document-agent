# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Run the FastAPI server
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Run with Docker
docker compose up

# Ingest documents from CLI
python scripts/ingest_cli.py                    # all files in data/docs/
python scripts/ingest_cli.py path/to/file.pdf   # single file
python scripts/ingest_cli.py path/to/file.pdf --force  # re-ingest

# Run all tests
pytest tests/ -v

# Run a single test file
pytest tests/test_validator.py

# Run a single test by name
pytest tests/test_validator.py::test_empty_file_fails

# Lint
ruff check src/ api/ scripts/ tests/

# Lint and auto-fix
ruff check src/ api/ scripts/ tests/ --fix

# Benchmark
python scripts/benchmark.py
```

## Architecture

Local RAG system: ingest documents → chunk → embed → store in ChromaDB → query with Ollama LLM.

### Two packages

- **`src/`** — core logic, no HTTP concerns. Modules: `ingestor.py` (load → chunk → embed → store), `retriever.py` (ChromaDB queries), `generator.py` (Ollama LLM calls), `pipeline.py` (retriever → generator), `validator.py` (file checks), `registry.py` (tracks indexed docs in JSON), `logger.py` (centralized logging).
- **`api/`** — FastAPI layer. `main.py` (app, CORS, dotenv), `routes.py` (4 endpoints: `/ingest`, `/query`, `/documents`, `/health`). Routes call into `src/` — no business logic in the API layer.

### Data flow

Ingestion: file → `validator` → `ingestor.load_document` → `ingestor.chunk_text` → OllamaEmbeddings → ChromaDB → `registry.add_entry`

Query: question → `retriever.get_relevant_chunks` (ChromaDB similarity search) → `generator.generate_answer` (Ollama LLM) → response

### Configuration

All config via environment variables loaded from `.env` by `python-dotenv`. See `.env.example` for every variable. No hardcoded paths, model names, or ports anywhere — every value uses `os.getenv()` with a fallback default.

### Key conventions

- `pythonpath` is set to repo root in `pyproject.toml` so `from src.xxx` and `from api.xxx` work everywhere.
- `src/__init__.py` calls `load_dotenv()` so env vars are available on first import.
- Every module uses `from src.logger import get_logger; logger = get_logger(__name__)`.
- Tests mock all external services (Ollama, ChromaDB) — no running services needed for `pytest`.
