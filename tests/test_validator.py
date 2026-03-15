import os
import tempfile

from src.validator import validate_file


def test_valid_pdf_passes():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4 fake content")
        path = f.name
    valid, reason = validate_file(path)
    assert valid is True
    assert reason == ""
    os.unlink(path)


def test_nonexistent_file_fails():
    valid, reason = validate_file("does_not_exist.pdf")
    assert valid is False
    assert "not found" in reason.lower()


def test_unsupported_extension_fails():
    with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as f:
        f.write(b"fake binary")
        path = f.name
    valid, reason = validate_file(path)
    assert valid is False
    assert "unsupported" in reason.lower()
    os.unlink(path)


def test_empty_file_fails():
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        path = f.name
    valid, reason = validate_file(path)
    assert valid is False
    assert "empty" in reason.lower()
    os.unlink(path)
