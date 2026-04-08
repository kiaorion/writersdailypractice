#!/usr/bin/env python3
"""
Pattern test suite.

Validates that:
  1. Every pattern in the YAML library matches its example "bad" cases
  2. Every "should_match" fixture triggers the expected pattern
  3. No "should_not_match" fixture triggers any pattern (no false positives)

Run with: python3 test_patterns.py
Exits 0 on success, 1 on any test failure.
"""

import sys
import json
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip3 install pyyaml")
    sys.exit(2)


SCRIPT_DIR = Path(__file__).resolve().parent
PIPELINE_DIR = SCRIPT_DIR.parent
PATTERNS_FILE = PIPELINE_DIR / "patterns.yaml"
FIXTURES_FILE = SCRIPT_DIR / "fixtures.json"


def load_patterns():
    with open(PATTERNS_FILE) as f:
        data = yaml.safe_load(f)
    return data["patterns"]


def load_fixtures():
    with open(FIXTURES_FILE) as f:
        return json.load(f)


def test_pattern_examples(patterns):
    """Each pattern's own example.bad should match its regex."""
    failures = []
    for p in patterns:
        rx = re.compile(p["regex"])
        for ex in p.get("examples", []):
            bad = ex.get("bad", "")
            if not rx.search(bad):
                failures.append({
                    "test": "pattern self-test",
                    "pattern_id": p["id"],
                    "expected_match": True,
                    "text": bad,
                })
            good = ex.get("good", "")
            if good and rx.search(good):
                failures.append({
                    "test": "pattern self-test (good example matched)",
                    "pattern_id": p["id"],
                    "expected_match": False,
                    "text": good,
                })
    return failures


def test_should_match(patterns, fixtures):
    """Every should_match fixture should be caught by the named pattern."""
    failures = []
    pattern_lookup = {p["id"]: re.compile(p["regex"]) for p in patterns}

    for f in fixtures.get("should_match", []):
        pid = f["pattern_id"]
        text = f["text"]
        if pid not in pattern_lookup:
            failures.append({
                "test": "should_match",
                "pattern_id": pid,
                "error": f"pattern_id '{pid}' not found in YAML",
            })
            continue
        if not pattern_lookup[pid].search(text):
            failures.append({
                "test": "should_match",
                "pattern_id": pid,
                "expected_match": True,
                "text": text,
            })
    return failures


def test_should_not_match(patterns, fixtures):
    """Every should_not_match fixture should NOT trigger any pattern."""
    failures = []
    compiled = [(p["id"], re.compile(p["regex"])) for p in patterns]

    for f in fixtures.get("should_not_match", []):
        text = f["text"]
        desc = f.get("description", text[:50])
        for pid, rx in compiled:
            m = rx.search(text)
            if m:
                failures.append({
                    "test": "should_not_match (false positive)",
                    "pattern_id": pid,
                    "description": desc,
                    "matched": m.group(0),
                    "text": text,
                })
    return failures


def main():
    print("Loading patterns and fixtures...")
    patterns = load_patterns()
    fixtures = load_fixtures()
    print(f"  {len(patterns)} patterns loaded")
    print(f"  {len(fixtures.get('should_match', []))} should_match fixtures")
    print(f"  {len(fixtures.get('should_not_match', []))} should_not_match fixtures")
    print()

    all_failures = []

    print("Running pattern self-tests (each pattern matches its own examples)...")
    failures = test_pattern_examples(patterns)
    if failures:
        print(f"  FAIL: {len(failures)} self-test failures")
        all_failures.extend(failures)
    else:
        print("  PASS")

    print("Running should_match fixtures...")
    failures = test_should_match(patterns, fixtures)
    if failures:
        print(f"  FAIL: {len(failures)} should_match failures")
        all_failures.extend(failures)
    else:
        print("  PASS")

    print("Running should_not_match fixtures (false positive check)...")
    failures = test_should_not_match(patterns, fixtures)
    if failures:
        print(f"  FAIL: {len(failures)} false positives")
        all_failures.extend(failures)
    else:
        print("  PASS")

    print()
    print("=" * 70)

    if all_failures:
        print(f"\n{len(all_failures)} test failures:\n")
        for i, f in enumerate(all_failures, 1):
            print(f"  [{i}] {f.get('test', 'unknown')}")
            for k, v in f.items():
                if k == "test":
                    continue
                print(f"        {k}: {v}")
            print()
        sys.exit(1)
    else:
        print("\nALL TESTS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
