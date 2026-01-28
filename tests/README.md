# Tests

Automated tests for Sovereign Document Agent.

## Running Tests

### Run all tests:
```bash
pytest tests/ -v
```

### Run specific test file:
```bash
pytest tests/test_governance.py -v
```

### Run with coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

## Test Structure

- `test_governance.py` - Tests for governance layer
- `test_pdf_reader.py` - Tests for PDF processing

## Test Coverage

Current coverage: 9 tests
- Governance: 5 tests
- PDF Reader: 4 tests

All tests passing ✅
