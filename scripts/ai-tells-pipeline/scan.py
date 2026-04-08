#!/usr/bin/env python3
"""
AI Tells Scanner
================

Reads patterns.yaml and scans HTML files for AI writing tells.
Outputs structured findings: file, line number, pattern id, severity, context.

Usage:
    python3 scan.py <file_or_glob> [...]
    python3 scan.py --all                # scan everything in scan_glob from config
    python3 scan.py --json <files>       # output as JSON instead of text
    python3 scan.py --exit-on-fail       # exit code 1 if any critical/high matches

Examples:
    python3 scan.py ../../writers-routines/ernest-hemingway/index.html
    python3 scan.py --all
    python3 scan.py --all --exit-on-fail
"""

import sys
import re
import os
import json
import glob as globlib
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip3 install pyyaml")
    sys.exit(2)


SCRIPT_DIR = Path(__file__).resolve().parent
PATTERNS_FILE = SCRIPT_DIR / "patterns.yaml"
REPO_ROOT = SCRIPT_DIR.parent.parent  # writersdailypractice/


def load_patterns():
    """Load and compile patterns from YAML."""
    with open(PATTERNS_FILE) as f:
        data = yaml.safe_load(f)

    compiled = []
    for p in data["patterns"]:
        compiled.append({
            "id": p["id"],
            "name": p["name"],
            "category": p["category"],
            "severity": p["severity"],
            "description": p["description"],
            "fix_strategy": p["fix_strategy"],
            "examples": p.get("examples", []),
            "regex": re.compile(p["regex"]),
            "raw_regex": p["regex"],
        })

    return compiled, data.get("config", {})


def strip_html_tags(text):
    """Strip HTML tags so we don't false-positive on attributes/scripts."""
    # Remove script and style blocks entirely
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    return text


def scan_file(filepath, patterns):
    """Scan a single file. Returns list of findings."""
    findings = []

    try:
        with open(filepath) as f:
            content = f.read()
    except (FileNotFoundError, IsADirectoryError):
        return findings

    # Build a list of (line_number, line_text) for both raw and stripped versions
    raw_lines = content.split("\n")

    # We scan the raw content but skip HTML attribute lines for em-dashes etc
    # by stripping tags only when checking
    for line_num, line in enumerate(raw_lines, start=1):
        # Skip lines that are pure HTML structure (no visible text)
        text_only = re.sub(r"<[^>]+>", " ", line).strip()
        if not text_only:
            continue

        for p in patterns:
            for match in p["regex"].finditer(line):
                findings.append({
                    "file": str(filepath),
                    "line": line_num,
                    "column": match.start(),
                    "pattern_id": p["id"],
                    "pattern_name": p["name"],
                    "category": p["category"],
                    "severity": p["severity"],
                    "matched_text": match.group(0),
                    "context": line.strip()[:200],
                })

    return findings


def expand_paths(paths, config):
    """Expand globs and handle --all."""
    expanded = []
    for path in paths:
        if path == "--all":
            scan_glob = config.get("scan_glob", "writers-routines/*/index.html")
            exclude_pattern = config.get("exclude_pattern", "")
            full_glob = str(REPO_ROOT / scan_glob)
            for f in globlib.glob(full_glob):
                if exclude_pattern and re.search(exclude_pattern, f):
                    continue
                expanded.append(f)
        elif "*" in path:
            expanded.extend(globlib.glob(path))
        else:
            expanded.append(path)
    return sorted(set(expanded))


def format_text_report(findings):
    """Format findings as human-readable text."""
    if not findings:
        return "[CLEAN] No AI tells found."

    by_file = {}
    for f in findings:
        by_file.setdefault(f["file"], []).append(f)

    out = []
    out.append(f"\nFound {len(findings)} AI tell(s) across {len(by_file)} file(s)\n")
    out.append("=" * 70)

    severity_counts = {"critical": 0, "high": 0, "medium": 0}
    for f in findings:
        severity_counts[f["severity"]] = severity_counts.get(f["severity"], 0) + 1

    out.append(f"  CRITICAL: {severity_counts['critical']}")
    out.append(f"  HIGH:     {severity_counts['high']}")
    out.append(f"  MEDIUM:   {severity_counts['medium']}")
    out.append("")

    for filepath, items in sorted(by_file.items()):
        rel = os.path.relpath(filepath, REPO_ROOT)
        out.append(f"\n{rel}")
        out.append("-" * 70)
        for item in sorted(items, key=lambda x: x["line"]):
            sev_marker = {
                "critical": "[!]",
                "high": "[>]",
                "medium": "[.]",
            }.get(item["severity"], "[?]")
            out.append(f"  {sev_marker} L{item['line']}  {item['pattern_name']}")
            out.append(f"      matched: \"{item['matched_text']}\"")
            ctx = item["context"]
            if len(ctx) > 120:
                ctx = ctx[:120] + "..."
            out.append(f"      context: {ctx}")
            out.append("")

    out.append("=" * 70)
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Scan files for AI writing tells")
    parser.add_argument("paths", nargs="*", help="Files or globs to scan (or --all)")
    parser.add_argument("--all", action="store_true", help="Scan all files matching config glob")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--exit-on-fail", action="store_true", help="Exit code 1 if any critical/high matches")
    args = parser.parse_args()

    patterns, config = load_patterns()

    paths = args.paths[:]
    if args.all:
        paths.append("--all")

    if not paths:
        parser.print_help()
        sys.exit(0)

    files = expand_paths(paths, config)

    all_findings = []
    for f in files:
        all_findings.extend(scan_file(f, patterns))

    if args.json:
        print(json.dumps({
            "files_scanned": len(files),
            "findings_count": len(all_findings),
            "findings": all_findings,
        }, indent=2))
    else:
        print(format_text_report(all_findings))
        print(f"\nFiles scanned: {len(files)}")

    if args.exit_on_fail:
        critical_or_high = [f for f in all_findings if f["severity"] in ("critical", "high")]
        if critical_or_high:
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
