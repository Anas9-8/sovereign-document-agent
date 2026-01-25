# German NER - Named Entity Recognition for German documents
# Using German BERT model
# Author: Anas
# Date: 2026-01-25

from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import re

def load_german_ner():
    """
    Load German NER model.
    Uses a pre-trained German BERT model for entity recognition.
    
    Returns:
        pipeline: NER pipeline
    """
    print("Loading German NER model...")
    
    try:
        # Use German NER model
        model_name = "dbmdz/bert-large-cased-finetuned-conll03-german"
        
        ner_pipeline = pipeline(
            "ner",
            model=model_name,
            aggregation_strategy="simple"
        )
        
        print("✅ German NER model loaded successfully!")
        return ner_pipeline
        
    except Exception as e:
        print(f"Warning: Could not load German NER model: {e}")
        print("Falling back to basic extraction...")
        return None

def extract_entities_ner(text, ner_pipeline):
    """
    Extract entities using German NER model.
    
    Args:
        text (str): Text to analyze
        ner_pipeline: NER pipeline
        
    Returns:
        dict: Extracted entities
    """
    if not ner_pipeline:
        return {}
    
    try:
        # Run NER
        entities = ner_pipeline(text)
        
        # Organize by type
        organized = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'miscellaneous': []
        }
        
        for entity in entities:
            entity_type = entity['entity_group']
            entity_text = entity['word']
            
            if entity_type == 'PER':
                organized['persons'].append(entity_text)
            elif entity_type == 'ORG':
                organized['organizations'].append(entity_text)
            elif entity_type == 'LOC':
                organized['locations'].append(entity_text)
            else:
                organized['miscellaneous'].append(entity_text)
        
        return organized
        
    except Exception as e:
        print(f"Error in NER: {e}")
        return {}

def extract_amounts_regex(text):
    """
    Extract monetary amounts using regex patterns.
    Handles German number formatting (7.199,50 €)
    
    Args:
        text (str): Text to analyze
        
    Returns:
        list: Found amounts
    """
    # Pattern for German amounts: 1.234,56 € or 1234,56 €
    pattern = r'\d{1,3}(?:\.\d{3})*,\d{2}\s*€'
    
    amounts = re.findall(pattern, text)
    return amounts

def extract_dates_regex(text):
    """
    Extract dates from German text.
    Handles formats like: 15. Januar 2024
    
    Args:
        text (str): Text to analyze
        
    Returns:
        list: Found dates
    """
    # Pattern for German dates
    patterns = [
        r'\d{1,2}\.\s*\w+\s*\d{4}',  # 15. Januar 2024
        r'\d{2}\.\d{2}\.\d{4}',       # 15.01.2024
    ]
    
    dates = []
    for pattern in patterns:
        found = re.findall(pattern, text)
        dates.extend(found)
    
    return dates

def extract_invoice_numbers(text):
    """
    Extract invoice numbers from German invoices.
    Patterns: RE-2024-001234, etc.
    
    Args:
        text (str): Text to analyze
        
    Returns:
        list: Found invoice numbers
    """
    # Common German invoice number patterns
    patterns = [
        r'RE-\d{4}-\d+',           # RE-2024-001234
        r'RG-\d+',                  # RG-123456
        r'Rechnung[:\s]+\w+-\d+',  # Rechnung: ABC-123
    ]
    
    numbers = []
    for pattern in patterns:
        found = re.findall(pattern, text)
        numbers.extend(found)
    
    return numbers

def analyze_german_document(text):
    """
    Complete analysis of German document.
    Combines NER + regex patterns.
    
    Args:
        text (str): Document text
        
    Returns:
        dict: Complete analysis
    """
    print("=" * 60)
    print("GERMAN NLP ANALYSIS")
    print("=" * 60)
    
    results = {}
    
    # Extract using regex (fast, reliable)
    print("\n1. Extracting structured data (regex)...")
    results['invoice_numbers'] = extract_invoice_numbers(text)
    results['amounts'] = extract_amounts_regex(text)
    results['dates'] = extract_dates_regex(text)
    
    print(f"   Found {len(results['invoice_numbers'])} invoice number(s)")
    print(f"   Found {len(results['amounts'])} amount(s)")
    print(f"   Found {len(results['dates'])} date(s)")
    
    # Extract using NER (optional - only if model available)
    print("\n2. Extracting entities (German NER)...")
    ner_pipeline = load_german_ner()
    
    if ner_pipeline:
        entities = extract_entities_ner(text, ner_pipeline)
        results['entities'] = entities
        
        print(f"   Found {len(entities['persons'])} person(s)")
        print(f"   Found {len(entities['organizations'])} organization(s)")
        print(f"   Found {len(entities['locations'])} location(s)")
    else:
        results['entities'] = None
        print("   NER skipped (model not available)")
    
    return results

def display_results(results):
    """
    Display analysis results.
    
    Args:
        results (dict): Analysis results
    """
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    
    print("\n📄 Invoice Numbers:")
    for num in results.get('invoice_numbers', []):
        print(f"   • {num}")
    
    print("\n💰 Amounts:")
    for amount in results.get('amounts', []):
        print(f"   • {amount}")
    
    print("\n📅 Dates:")
    for date in results.get('dates', []):
        print(f"   • {date}")
    
    if results.get('entities'):
        entities = results['entities']
        
        print("\n👤 Persons:")
        for person in entities.get('persons', []):
            print(f"   • {person}")
        
        print("\n🏢 Organizations:")
        for org in entities.get('organizations', []):
            print(f"   • {org}")
        
        print("\n📍 Locations:")
        for loc in entities.get('locations', []):
            print(f"   • {loc}")
    
    print("\n" + "=" * 60)

def main():
    """Main function"""
    print("=" * 60)
    print("GERMAN NLP PROCESSOR")
    print("=" * 60)
    
    # Read extracted text
    text_file = "extracted_text.txt"
    
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: {text_file} not found!")
        print("Please run pdf_reader.py first.")
        return
    
    print(f"\nDocument length: {len(text)} characters")
    
    # Analyze document
    results = analyze_german_document(text)
    
    # Display results
    display_results(results)
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()
