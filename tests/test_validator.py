"""Tests for file validation."""

import os
import tempfile

from src.validator import validate_file


def test_valid_pdf_passes():
    """A real PDF file should pass validation."""
    if not os.path.exists("rechnung_beispiel.pdf"):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4 fake content")
            path = f.name
    else:
        path = "rechnung_beispiel.pdf"

    valid, reason = validate_file(path)
    assert valid is True
    assert reason == ""


def test_nonexistent_file_fails():
    """A missing file should fail."""
    valid, reason = validate_file("does_not_exist.pdf")
    assert valid is False
    assert "not found" in reason.lower()


def test_unsupported_extension_fails():
    """A .exe file should be rejected."""
    with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as f:
        f.write(b"fake binary")
        path = f.name

    valid, reason = validate_file(path)
    assert valid is False
    assert "unsupported" in reason.lower()
    os.unlink(path)


def test_empty_file_fails():
    """A zero-byte file should be rejected."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        path = f.name

    valid, reason = validate_file(path)
    assert valid is False
    assert "empty" in reason.lower()
    os.unlink(path)
