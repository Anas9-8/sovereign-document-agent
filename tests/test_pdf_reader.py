# Tests for PDF Reader
# Testing PDF extraction functionality

import pytest
from pypdf import PdfReader
import os


def test_pdf_exists():
    """Test that sample PDF exists"""
    assert os.path.exists("rechnung_beispiel.pdf"), "Sample PDF not found"


def test_pdf_can_be_read():
    """Test that PDF can be opened"""
    try:
        reader = PdfReader("rechnung_beispiel.pdf")
        assert len(reader.pages) > 0, "PDF has no pages"
    except Exception as e:
        pytest.fail(f"Failed to read PDF: {e}")


def test_pdf_text_extraction():
    """Test that text can be extracted from PDF"""
    reader = PdfReader("rechnung_beispiel.pdf")
    text = reader.pages[0].extract_text()

    assert len(text) > 0, "No text extracted"
    assert len(text) > 500, "Text too short"


def test_pdf_contains_invoice_data():
    """Test that PDF contains expected invoice data"""
    reader = PdfReader("rechnung_beispiel.pdf")
    text = reader.pages[0].extract_text()

    # Check for key invoice elements
    assert "RE-2024-001234" in text, "Invoice number not found"
    assert (
        "TechSolutions" in text or "Mustermann" in text
    ), "Company/customer name not found"
    assert "€" in text or "EUR" in text, "Currency symbol not found"
