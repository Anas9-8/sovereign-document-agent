# Governance Layer - GDPR & EU AI Act Compliance
# Logging, Human-in-the-Loop, Audit Trail, Guardrails
# Author: Anas
# Date: 2026-01-25

import logging
import json
import os
from datetime import datetime
from pathlib import Path

# Configure logging
LOG_FILE = "system.log"
AUDIT_FILE = "audit_trail.json"

# Set up logger
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()  # Also print to console
    ]
)

logger = logging.getLogger(__name__)

# Guardrails configuration
GUARDRAILS = {
    'max_file_size_mb': 10,
    'allowed_extensions': ['.pdf'],
    'require_human_approval_keywords': ['vertraulich', 'confidential', 'secret', 'geheim'],
}

class AuditTrail:
    """
    Manages audit trail for compliance.
    Records all operations in JSON format.
    """
    
    def __init__(self, audit_file=AUDIT_FILE):
        self.audit_file = audit_file
        
        # Create file if doesn't exist
        if not os.path.exists(audit_file):
            with open(audit_file, 'w') as f:
                json.dump([], f)
    
    def log_event(self, action, details, status='success'):
        """
        Log an event to audit trail.
        
        Args:
            action (str): Action performed
            details (dict): Additional details
            status (str): 'success' or 'failure'
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'status': status,
            'details': details
        }
        
        # Read existing events
        try:
            with open(self.audit_file, 'r') as f:
                events = json.load(f)
        except:
            events = []
        
        # Add new event
        events.append(event)
        
        # Write back
        with open(self.audit_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Audit: {action} - {status}")

# Global audit trail instance
audit = AuditTrail()

def check_file_guardrails(file_path):
    """
    Check if file meets guardrail requirements.
    
    Args:
        file_path (str): Path to file
        
    Returns:
        tuple: (passed: bool, message: str)
    """
    logger.info(f"Checking guardrails for: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        msg = f"File not found: {file_path}"
        logger.error(msg)
        audit.log_event('guardrail_check', {'file': file_path, 'reason': 'not_found'}, 'failure')
        return False, msg
    
    # Check file extension
    file_ext = Path(file_path).suffix.lower()
    if file_ext not in GUARDRAILS['allowed_extensions']:
        msg = f"File type not allowed: {file_ext}. Allowed: {GUARDRAILS['allowed_extensions']}"
        logger.error(msg)
        audit.log_event('guardrail_check', {'file': file_path, 'reason': 'invalid_extension'}, 'failure')
        return False, msg
    
    # Check file size
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    max_size = GUARDRAILS['max_file_size_mb']
    
    if file_size_mb > max_size:
        msg = f"File too large: {file_size_mb:.2f}MB > {max_size}MB limit"
        logger.error(msg)
        audit.log_event('guardrail_check', {'file': file_path, 'size_mb': file_size_mb, 'reason': 'too_large'}, 'failure')
        return False, msg
    
    logger.info(f"✅ Guardrails passed: {file_path} ({file_size_mb:.2f}MB)")
    audit.log_event('guardrail_check', {'file': file_path, 'size_mb': file_size_mb}, 'success')
    return True, "OK"

def check_content_sensitivity(text):
    """
    Check if content contains sensitive keywords.
    
    Args:
        text (str): Text to check
        
    Returns:
        tuple: (is_sensitive: bool, found_keywords: list)
    """
    keywords = GUARDRAILS['require_human_approval_keywords']
    text_lower = text.lower()
    
    found = [kw for kw in keywords if kw in text_lower]
    
    if found:
        logger.warning(f"⚠️  Sensitive content detected: {found}")
        return True, found
    
    return False, []

def request_human_approval(reason):
    """
    Request human approval for sensitive operation.
    
    Args:
        reason (str): Reason for approval request
        
    Returns:
        bool: True if approved, False otherwise
    """
    print("\n" + "=" * 60)
    print("🚨 HUMAN APPROVAL REQUIRED")
    print("=" * 60)
    print(f"Reason: {reason}")
    print("\nThis document may contain sensitive information.")
    print("GDPR requires explicit consent for processing.")
    print("=" * 60)
    
    logger.warning(f"Human approval requested: {reason}")
    audit.log_event('approval_requested', {'reason': reason}, 'pending')
    
    # Ask for approval
    while True:
        response = input("\n❓ Do you approve processing? (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            logger.info("✅ Human approval GRANTED")
            audit.log_event('approval_decision', {'decision': 'approved', 'reason': reason}, 'success')
            return True
        elif response in ['no', 'n']:
            logger.info("❌ Human approval DENIED")
            audit.log_event('approval_decision', {'decision': 'denied', 'reason': reason}, 'success')
            return False
        else:
            print("Please answer 'yes' or 'no'")

def log_processing_start(file_path):
    """Log start of document processing."""
    logger.info(f"📄 Processing started: {file_path}")
    audit.log_event('processing_start', {'file': file_path}, 'success')

def log_processing_end(file_path, success=True, extracted_fields=0):
    """Log end of document processing."""
    status = 'success' if success else 'failure'
    logger.info(f"{'✅' if success else '❌'} Processing completed: {file_path}")
    audit.log_event(
        'processing_end',
        {'file': file_path, 'extracted_fields': extracted_fields},
        status
    )

def log_ai_extraction(model, success=True, fields_extracted=0):
    """Log AI extraction operation."""
    status = 'success' if success else 'failure'
    logger.info(f"AI extraction ({model}): {fields_extracted} fields - {status}")
    audit.log_event(
        'ai_extraction',
        {'model': model, 'fields_extracted': fields_extracted},
        status
    )

def get_audit_summary():
    """
    Get summary of audit trail.
    
    Returns:
        dict: Summary statistics
    """
    try:
        with open(AUDIT_FILE, 'r') as f:
            events = json.load(f)
    except:
        return {'total_events': 0}
    
    summary = {
        'total_events': len(events),
        'success_count': len([e for e in events if e['status'] == 'success']),
        'failure_count': len([e for e in events if e['status'] == 'failure']),
        'actions': {}
    }
    
    # Count by action type
    for event in events:
        action = event['action']
        summary['actions'][action] = summary['actions'].get(action, 0) + 1
    
    return summary

def print_governance_report():
    """Print governance compliance report."""
    print("\n" + "=" * 60)
    print("📊 GOVERNANCE COMPLIANCE REPORT")
    print("=" * 60)
    
    summary = get_audit_summary()
    
    print(f"\n📁 Log Files:")
    print(f"   • System log: {LOG_FILE}")
    print(f"   • Audit trail: {AUDIT_FILE}")
    
    print(f"\n📈 Statistics:")
    print(f"   • Total events: {summary['total_events']}")
    print(f"   • Successful: {summary['success_count']}")
    print(f"   • Failed: {summary['failure_count']}")
    
    print(f"\n🔧 Actions logged:")
    for action, count in summary['actions'].items():
        print(f"   • {action}: {count}")
    
    print(f"\n🛡️  Guardrails:")
    print(f"   • Max file size: {GUARDRAILS['max_file_size_mb']}MB")
    print(f"   • Allowed types: {', '.join(GUARDRAILS['allowed_extensions'])}")
    print(f"   • Sensitive keywords: {len(GUARDRAILS['require_human_approval_keywords'])}")
    
    print("\n" + "=" * 60)

def main():
    """Test governance system."""
    print("=" * 60)
    print("GOVERNANCE SYSTEM TEST")
    print("=" * 60)
    
    # Test guardrails
    print("\n1. Testing guardrails...")
    passed, msg = check_file_guardrails("rechnung_beispiel.pdf")
    print(f"   Result: {msg}")
    
    # Test content sensitivity
    print("\n2. Testing content sensitivity...")
    test_text = "This is a confidential document with secret information."
    is_sensitive, keywords = check_content_sensitivity(test_text)
    if is_sensitive:
        print(f"   ⚠️  Sensitive keywords found: {keywords}")
    else:
        print(f"   ✅ No sensitive content detected")
    
    # Print report
    print_governance_report()

if __name__ == "__main__":
    main()
