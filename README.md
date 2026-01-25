# Sovereign Document Agent

Local AI system for processing German PDF documents with GDPR compliance.

## Current Status: Sprint 2 Complete ✅

### Features Implemented
- ✅ PDF document reading (pypdf)
- ✅ German text extraction
- ✅ Multi-page support
- ✅ Error handling
- ✅ Text output to file

### Coming Next
- 🔄 Local LLM integration (Ollama)
- 🔄 Information extraction (invoice numbers, dates, amounts)
- 🔄 German NLP models
- 🔄 Governance layer
- 🔄 Streamlit UI

## Tech Stack
- **Language:** Python 3
- **OS:** Ubuntu/WSL
- **PDF Processing:** pypdf
- **Version Control:** Git/GitHub

## Setup

### 1. Clone repository
```bash
git clone https://github.com/anas9-8/sovereign-document-agent.git
cd sovereign-document-agent
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Read PDF document
```bash
python pdf_reader.py
```

This will:
1. Read `rechnung_beispiel.pdf`
2. Extract all text
3. Save to `extracted_text.txt`

## Project Structure
```
sovereign-document-agent/
├── pdf_reader.py           # PDF reading module
├── rechnung_beispiel.pdf   # Sample German invoice
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── venv/                  # Virtual environment
```

## Author
Anas - ML Engineering Weiterbildung

## License
MIT
