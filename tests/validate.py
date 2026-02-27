#!/usr/bin/env python3
"""
OpenVIP Test Suite Validator

Validates test cases against the OpenVIP JSON Schema.
Usage: python validate.py [--schema PATH] [--tests PATH]
"""

import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("Error: jsonschema package required. Install with: pip install jsonschema")
    sys.exit(1)


def load_schema(schema_path: Path) -> dict:
    """Load JSON Schema from file."""
    with open(schema_path) as f:
        return json.load(f)


def load_tests(tests_dir: Path) -> list:
    """Load all test files from directory."""
    tests = []
    for test_file in tests_dir.glob("*.json"):
        with open(test_file) as f:
            data = json.load(f)
            for group in data:
                for test in group.get("tests", []):
                    tests.append({
                        "file": test_file.name,
                        "group": group.get("description", "unknown"),
                        "description": test.get("description", "unknown"),
                        "data": test.get("data"),
                        "expected_valid": test.get("valid", True)
                    })
    return tests


def validate_message(schema: dict, data: dict) -> tuple[bool, str]:
    """Validate a message against schema. Returns (is_valid, error_message)."""
    try:
        jsonschema.validate(data, schema)
        return True, ""
    except jsonschema.ValidationError as e:
        return False, str(e.message)


def run_tests(schema: dict, tests: list) -> tuple[int, int, list]:
    """Run all tests. Returns (passed, failed, failures)."""
    passed = 0
    failed = 0
    failures = []

    for test in tests:
        is_valid, error = validate_message(schema, test["data"])

        if is_valid == test["expected_valid"]:
            passed += 1
        else:
            failed += 1
            failures.append({
                "file": test["file"],
                "group": test["group"],
                "description": test["description"],
                "expected_valid": test["expected_valid"],
                "actual_valid": is_valid,
                "error": error
            })

    return passed, failed, failures


def main():
    # Default paths
    spec_dir = Path(__file__).parent.parent
    schema_path = spec_dir / "schema" / "v1.0.json"
    tests_dir = Path(__file__).parent / "schema"

    # Parse args
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--schema" and i + 1 < len(args):
            schema_path = Path(args[i + 1])
            i += 2
        elif args[i] == "--tests" and i + 1 < len(args):
            tests_dir = Path(args[i + 1])
            i += 2
        else:
            i += 1

    # Load schema and tests
    print(f"Loading schema: {schema_path}")
    schema = load_schema(schema_path)

    print(f"Loading tests: {tests_dir}")
    tests = load_tests(tests_dir)
    print(f"Found {len(tests)} test cases\n")

    # Run tests
    passed, failed, failures = run_tests(schema, tests)

    # Report
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    if failures:
        print("\nFAILURES:\n")
        for f in failures:
            print(f"  [{f['file']}] {f['group']}")
            print(f"    Test: {f['description']}")
            print(f"    Expected valid: {f['expected_valid']}, Actual valid: {f['actual_valid']}")
            if f['error']:
                print(f"    Error: {f['error']}")
            print()

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
