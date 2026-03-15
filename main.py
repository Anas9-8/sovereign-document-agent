# Main Pipeline - Sovereign Document Agent
# Integrates: PDF Reading + AI Extraction + German NLP + Governance
# Author: Asmar
# Date: 2025-01-24

import sys
from pypdf import PdfReader
import governance
import json


def read_pdf_with_governance(pdf_file):
    """
    Read PDF with governance checks.

    Args:
        pdf_file (str): Path to PDF

    Returns:
        str: Extracted text or None
    """
    print("=" * 60)
    print("STEP 1: PDF READING WITH GOVERNANCE")
    print("=" * 60)

    # Check guardrails
    passed, msg = governance.check_file_guardrails(pdf_file)

    if not passed:
        print(f"\n❌ Guardrail check failed: {msg}")
        return None

    print(f"✅ Guardrails passed: {pdf_file}")

    # Log processing start
    governance.log_processing_start(pdf_file)

    try:
        # Read PDF
        reader = PdfReader(pdf_file)
        num_pages = len(reader.pages)

        print(f"\n📄 Reading PDF...")
        print(f"   Pages: {num_pages}")

        # Extract text
        full_text = ""
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            full_text += text + "\n"

        print(f"   Extracted: {len(full_text)} characters")

        # Log success
        governance.log_processing_end(pdf_file, success=True)

        return full_text

    except Exception as e:
        print(f"\n❌ Error reading PDF: {e}")
        governance.log_processing_end(pdf_file, success=False)
        return None


def check_sensitivity_and_approve(text):
    """
    Check for sensitive content and request approval if needed.

    Args:
        text (str): Document text

    Returns:
        bool: True if approved to continue
    """
    print("\n" + "=" * 60)
    print("STEP 2: SENSITIVITY CHECK")
    print("=" * 60)

    is_sensitive, keywords = governance.check_content_sensitivity(text)

    if is_sensitive:
        print(f"\n⚠️  Sensitive content detected: {keywords}")

        # Request human approval
        approved = governance.request_human_approval(
            f"Document contains sensitive keywords: {keywords}"
        )

        return approved
    else:
        print("\n✅ No sensitive content detected - safe to process")
        return True


def extract_with_ai(text):
    """
    Extract information using AI with governance logging.

    Args:
        text (str): Text to analyze

    Returns:
        dict: Extracted data
    """
    print("\n" + "=" * 60)
    print("STEP 3: AI EXTRACTION WITH GOVERNANCE")
    print("=" * 60)

    # Import here to avoid loading if not needed
    import ollama
    import re

    # Create prompt
    prompt = f"""
You are an AI assistant that extracts information from German invoices.

Extract the following information:
1. Invoice number (Rechnungsnummer)
2. Invoice date (Datum)
3. Customer name (Kunde)
4. Total amount (Gesamtbetrag)
5. Due date (Fälligkeitsdatum)

Return ONLY a JSON object with these keys:
- invoice_number
- invoice_date
- customer_name
- total_amount
- due_date

Invoice Text:
{text}

JSON Response:
"""

    print("Sending to AI model (LLaMA 3.2)...")
    print("(This may take 10-30 seconds...)")

    try:
        # Call AI
        response = ollama.generate(model="llama3.2:1b", prompt=prompt)

        ai_response = response["response"]

        # Clean and parse JSON
        start = ai_response.find("{")
        if start == -1:
            governance.log_ai_extraction(
                "llama3.2:1b", success=False, fields_extracted=0
            )
            return None

        json_str = ai_response[start:].strip()
        json_str = re.sub(r"\s+", " ", json_str)

        # Fix incomplete JSON
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            json_str = json_str.rstrip() + ("}" * (open_braces - close_braces))

        data = json.loads(json_str)

        # Log success
        governance.log_ai_extraction(
            "llama3.2:1b", success=True, fields_extracted=len(data)
        )

        print(f"\n✅ AI extraction successful!")
        print(f"   Fields extracted: {len(data)}")

        return data

    except Exception as e:
        print(f"\n❌ AI extraction failed: {e}")
        governance.log_ai_extraction("llama3.2:1b", success=False, fields_extracted=0)
        return None


def display_results(data):
    """Display extracted information."""
    if not data:
        print("\n❌ No data to display")
        return

    print("\n" + "=" * 60)
    print("EXTRACTED INFORMATION")
    print("=" * 60)
    print(f"Invoice Number:  {data.get('invoice_number', 'N/A')}")
    print(f"Invoice Date:    {data.get('invoice_date', 'N/A')}")
    print(f"Customer Name:   {data.get('customer_name', 'N/A')}")
    print(f"Total Amount:    {data.get('total_amount', 'N/A')}")
    print(f"Due Date:        {data.get('due_date', 'N/A')}")
    print("=" * 60)


def save_results(data, output_file):
    """Save results with governance logging."""
    if not data:
        return

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Results saved to: {output_file}")
    governance.audit.log_event("save_results", {"file": output_file}, "success")


def main():
    """Main pipeline with full governance."""
    print("\n" + "=" * 70)
    print("🛡️  SOVEREIGN DOCUMENT AGENT - WITH GOVERNANCE")
    print("=" * 70)
    print("\nGDPR-compliant document processing with audit trail")
    print("=" * 70)

    # Configuration
    pdf_file = "rechnung_beispiel.pdf"
    output_file = "final_results.json"

    # Step 1: Read PDF with governance
    text = read_pdf_with_governance(pdf_file)

    if not text:
        print("\n❌ Pipeline stopped - PDF reading failed")
        sys.exit(1)

    # Step 2: Check sensitivity and get approval
    approved = check_sensitivity_and_approve(text)

    if not approved:
        print("\n🛑 Pipeline stopped - Human approval denied")
        governance.audit.log_event(
            "pipeline_stopped", {"reason": "approval_denied"}, "success"
        )
        sys.exit(0)

    # Step 3: Extract with AI
    data = extract_with_ai(text)

    if not data:
        print("\n❌ Pipeline stopped - AI extraction failed")
        sys.exit(1)

    # Step 4: Display results
    display_results(data)

    # Step 5: Save results
    save_results(data, output_file)

    # Final governance report
    print("\n")
    governance.print_governance_report()

    print("\n✅ Pipeline completed successfully!")
    print("\n📊 Check these files:")
    print(f"   • {governance.LOG_FILE} - System logs")
    print(f"   • {governance.AUDIT_FILE} - Audit trail")
    print(f"   • {output_file} - Extracted data")
    print("=" * 70)


if __name__ == "__main__":
    main()
