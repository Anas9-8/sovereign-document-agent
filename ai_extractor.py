# AI Extractor - Extract structured information from documents
# Using local LLM (Ollama + LLaMA 3.2)
# Author: Asmar
# Date: 2025-01-24

import ollama
import json


def extract_invoice_info(text):
    """
    Extract structured information from invoice text using local LLM.

    Args:
        text (str): Extracted text from PDF

    Returns:
        dict: Structured information (invoice number, date, amount, etc.)
    """

    # Create prompt for LLM
    prompt = f"""
You are an AI assistant that extracts information from German invoices.

Extract the following information from the invoice text below:
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

If any information is not found, use "Not found" as the value.

Invoice Text:
{text}

JSON Response:
"""

    print("Sending to AI model...")
    print("(This may take 10-30 seconds...)")

    try:
        # Call Ollama API
        response = ollama.generate(model="llama3.2:1b", prompt=prompt)

        # Get response text
        ai_response = response["response"]

        print("\n--- AI Response ---")
        print(ai_response)
        print("-------------------\n")

        # Clean and fix JSON
        try:
            # Find JSON in response
            start = ai_response.find("{")

            if start == -1:
                print("Warning: No JSON found in response")
                return None

            # Extract from { onwards
            json_str = ai_response[start:].strip()

            # Clean multiple spaces (fix control character issues)
            import re

            json_str = re.sub(r"\s+", " ", json_str)

            # Fix incomplete JSON - count braces
            open_braces = json_str.count("{")
            close_braces = json_str.count("}")
            # Add missing closing braces
            if open_braces > close_braces:
                missing = open_braces - close_braces
                json_str = json_str.rstrip() + "\n" + ("}" * missing)
                print(f"Fixed: Added {missing} missing closing brace(s)")

            # Try to parse
            data = json.loads(json_str)
            return data

        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse JSON: {e}")
            print(f"Attempted to parse: {json_str[:200]}...")
            return None

    except Exception as e:
        print(f"Error calling AI model: {e}")
        return None


def format_output(data):
    """
    Format extracted data for display.

    Args:
        data (dict): Extracted information
    """
    if not data:
        print("No data extracted.")
        return

    print("=" * 60)
    print("EXTRACTED INFORMATION")
    print("=" * 60)
    print(f"Invoice Number:  {data.get('invoice_number', 'N/A')}")
    print(f"Invoice Date:    {data.get('invoice_date', 'N/A')}")
    print(f"Customer Name:   {data.get('customer_name', 'N/A')}")
    print(f"Total Amount:    {data.get('total_amount', 'N/A')}")
    print(f"Due Date:        {data.get('due_date', 'N/A')}")
    print("=" * 60)


def save_json(data, filename):
    """
    Save extracted data as JSON file.

    Args:
        data (dict): Data to save
        filename (str): Output filename
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nData saved to: {filename}")


def main():
    """Main function"""
    print("=" * 60)
    print("AI EXTRACTOR - Local LLM Information Extraction")
    print("=" * 60)
    print()

    # Read extracted text
    text_file = "extracted_text.txt"

    print(f"Reading: {text_file}")

    try:
        with open(text_file, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: {text_file} not found!")
        print("Please run pdf_reader.py first.")
        return

    print(f"Text length: {len(text)} characters")
    print()

    # Extract information using AI
    data = extract_invoice_info(text)

    if data:
        # Display results
        format_output(data)

        # Save to JSON
        save_json(data, "extracted_data.json")

        print("\nSuccess! Information extracted.")
    else:
        print("\nFailed to extract information.")
        print("The AI model may need a better prompt or more context.")


if __name__ == "__main__":
    main()
