# PDF Reader - Extract text from German invoices
# Author: Asmar
# Date: 2025-01-24

from pypdf import PdfReader
import sys

def read_pdf(pdf_path):
    """
    Read PDF file and extract text from all pages.
    
    Args:
        pdf_path (str): Path to PDF file
        
    Returns:
        str: Extracted text
    """
    try:
        # Open PDF file
        reader = PdfReader(pdf_path)
        
        # Get number of pages
        num_pages = len(reader.pages)
        print(f"Number of pages: {num_pages}")
        
        # Extract text from all pages
        full_text = ""
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            full_text += text + "\n"
        
        return full_text
        
    except FileNotFoundError:
        print(f"Error: File '{pdf_path}' not found!")
        return None
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def save_text(text, output_file):
    """
    Save extracted text to file.
    
    Args:
        text (str): Text to save
        output_file (str): Output filename
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Text saved to: {output_file}")

def main():
    """Main function"""
    # PDF file to read
    pdf_file = "rechnung_beispiel.pdf"
    
    # Output text file
    output_file = "extracted_text.txt"
    
    print("=" * 50)
    print("PDF Reader - German Document Processing")
    print("=" * 50)
    
    # Read PDF
    text = read_pdf(pdf_file)
    
    if text:
        # Print extracted text
        print("\n--- Extracted Text ---")
        print(text)
        
        # Save to file
        save_text(text, output_file)
        
        print("\n" + "=" * 50)
        print("Success!")
        print("=" * 50)
    else:
        print("Failed to extract text.")
        sys.exit(1)

if __name__ == "__main__":
    main()
