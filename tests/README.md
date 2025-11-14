# Test Suite for Tableau Data Assistant

## Overview

Comprehensive test suite covering all responsible AI modules.

## Running Tests

### Install Test Dependencies

```bash
pip install pytest pytest-cov
```

### Run All Tests

```bash
# From project root
cd tableau-data-assistant
python -m pytest tests/ -v
```

### Run Specific Test File

```bash
python -m pytest tests/test_validation.py -v
python -m pytest tests/test_privacy.py -v
python -m pytest tests/test_cleaning.py -v
python -m pytest tests/test_anomaly_detection.py -v
```

### Run with Coverage

```bash
python -m pytest tests/ --cov=utils --cov-report=html
```

## Test Coverage

### Validation Module (test_validation.py)
- ✅ Schema inference
- ✅ Data type validation
- ✅ Null threshold checking
- ✅ Duplicate detection
- ✅ Required columns validation
- ✅ Value range validation
- ✅ Uniqueness constraints

### Privacy Module (test_privacy.py)
- ✅ PII detection (keyword and pattern-based)
- ✅ Email/phone detection
- ✅ Partial, full, hash, and remove masking
- ✅ Data minimization (row limiting)
- ✅ Sampling methods (head, tail, random, stratified)
- ✅ Automatic PII masking before AI

### Cleaning Module (test_cleaning.py)
- ✅ Column name standardization
- ✅ Duplicate removal
- ✅ Whitespace trimming
- ✅ Empty row/column removal
- ✅ Row capping for performance
- ✅ Outlier detection and removal

### Anomaly Detection Module (test_anomaly_detection.py)
- ✅ IQR-based detection
- ✅ Z-score based detection
- ✅ Ensemble voting (majority, unanimous, any)
- ✅ Threshold sensitivity
- ✅ Outlier bounds calculation

## Adding New Tests

1. Create test file in `tests/` directory
2. Import pytest and the module to test
3. Create fixtures for test data
4. Write test classes and methods
5. Run tests to verify

Example:
```python
import pytest
from utils.your_module import YourClass

@pytest.fixture
def test_data():
    return {"key": "value"}

class TestYourClass:
    def test_method(self, test_data):
        obj = YourClass()
        result = obj.method(test_data)
        assert result is not None
```

## Test Data

All tests use synthetic data to avoid PII concerns. Do not use real data in tests.

## Continuous Integration

Tests can be integrated with CI/CD pipelines:

```yaml
# Example .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt pytest
      - run: python -m pytest tests/ -v
```
