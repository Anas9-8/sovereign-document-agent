"""Tests for ingestion pipeline (mocked, no Ollama/ChromaDB needed)."""

from unittest.mock import patch

from src.ingestor import chunk_text


def test_chunk_text_returns_list():
    """chunk_text should return a list of strings."""
    text = "Hello world. " * 100
    chunks = chunk_text(text)
    assert isinstance(chunks, list)
    assert all(isinstance(c, str) for c in chunks)


def test_chunk_text_respects_size():
    """Each chunk should not exceed CHUNK_SIZE (plus some overlap tolerance)."""
    text = "Word " * 500
    chunks = chunk_text(text)
    max_allowed = 500 + 100  # chunk size + tolerance for split boundaries
    for chunk in chunks:
        assert len(chunk) <= max_allowed


@patch("src.ingestor.registry")
def test_ingest_file_skips_if_already_indexed(mock_registry):
    """Already-indexed files should be skipped."""
    mock_registry.is_indexed.return_value = True

    from src.ingestor import ingest_file
    result = ingest_file("some_file.pdf")

    assert result["status"] == "skipped"
    assert result["chunks_created"] == 0
