# Tests for Governance Module
# Testing guardrails and audit functionality

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import governance
import json


def test_guardrail_check_valid_file():
    """Test guardrail check with valid PDF"""
    if not os.path.exists("rechnung_beispiel.pdf"):
        pytest.skip("Sample PDF not found")

    passed, msg = governance.check_file_guardrails("rechnung_beispiel.pdf")
    assert passed == True, f"Valid file failed guardrail: {msg}"


def test_guardrail_check_missing_file():
    """Test guardrail check with missing file"""
    passed, msg = governance.check_file_guardrails("nonexistent.pdf")
    assert passed == False, "Guardrail should fail for missing file"


def test_content_sensitivity_clean():
    """Test sensitivity check with clean content"""
    clean_text = "This is a normal invoice with standard content."
    is_sensitive, keywords = governance.check_content_sensitivity(clean_text)
    assert is_sensitive == False, "Clean text marked as sensitive"


def test_content_sensitivity_with_keywords():
    """Test sensitivity check with sensitive keywords"""
    sensitive_text = "This is a confidential document with secret information."
    is_sensitive, keywords = governance.check_content_sensitivity(sensitive_text)
    assert is_sensitive == True, "Sensitive content not detected"
    assert len(keywords) > 0, "No keywords found"


def test_audit_trail_creation():
    """Test that audit trail can be created"""
    audit = governance.AuditTrail("test_audit.json")

    # Clean up before test
    if os.path.exists("test_audit.json"):
        os.remove("test_audit.json")

    audit = governance.AuditTrail("test_audit.json")
    audit.log_event("test_action", {"test": "data"}, "success")

    assert os.path.exists("test_audit.json"), "Audit file not created"

    # Verify content
    with open("test_audit.json", "r") as f:
        events = json.load(f)

    assert len(events) > 0, "No events logged"
    assert events[0]["action"] == "test_action", "Event not logged correctly"

    # Cleanup
    os.remove("test_audit.json")
