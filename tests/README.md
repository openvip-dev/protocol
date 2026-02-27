# OpenVIP Test Suite

Conformance tests for validating OpenVIP implementations.

## Running Tests

### Prerequisites

```bash
pip install jsonschema
```

### Validate Examples

```bash
python tests/validate.py
```

### Custom Schema Path

```bash
python tests/validate.py --schema path/to/schema.json
```

## Test Format

Tests follow the JSON Schema Test Suite format:

```json
[
  {
    "description": "test group description",
    "tests": [
      {
        "description": "individual test description",
        "data": { ... },
        "valid": true
      }
    ]
  }
]
```

- `data`: The OpenVIP message to validate
- `valid`: `true` if the message should pass validation, `false` if it should fail
