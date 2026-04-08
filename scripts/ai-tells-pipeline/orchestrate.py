#!/usr/bin/env python3
"""
AI Tells Pipeline Orchestrator
==============================

The full scan -> rewrite -> re-scan loop. This script:

1. Runs scan.py on the target file(s)
2. If findings exist, builds a structured rewriter prompt with the findings
   and the pattern reference, dumps it to stdout (and optionally to a file)
3. The user/Claude takes that prompt and runs it through a constrained
   Sonnet rewriter agent
4. After the rewriter finishes, this script re-runs scan.py
5. Loops up to max_iterations times
6. If still dirty after max iterations, moves the file to needs-manual-review/

Usage:
    python3 orchestrate.py <file>                    # interactive single-file mode
    python3 orchestrate.py --all                     # full pipeline on all routine pages
    python3 orchestrate.py --build-prompt <file>     # just emit the rewriter prompt for a file
    python3 orchestrate.py --check                   # scan only, no rewrite (CI mode)

Notes:
- The actual rewrite step is performed by a separate Claude/Sonnet agent.
  This script does not call any LLM directly. It generates the prompts and
  validates the results. The user wires it into their Claude Code workflow.
"""

import sys
import os
import json
import argparse
import shutil
import subprocess
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip3 install pyyaml")
    sys.exit(2)


SCRIPT_DIR = Path(__file__).resolve().parent
PATTERNS_FILE = SCRIPT_DIR / "patterns.yaml"
PROMPT_TEMPLATE_FILE = SCRIPT_DIR / "rewriter_prompt_template.md"
NEEDS_REVIEW_DIR = SCRIPT_DIR / "needs-manual-review"
REPO_ROOT = SCRIPT_DIR.parent.parent


def load_patterns():
    with open(PATTERNS_FILE) as f:
        return yaml.safe_load(f)


def run_scan(file_path):
    """Invoke scan.py on a file and return findings as a list of dicts."""
    cmd = [
        sys.executable,
        str(SCRIPT_DIR / "scan.py"),
        str(file_path),
        "--json",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode not in (0, 1):
        print(f"ERROR running scan.py: {result.stderr}")
        return None
    try:
        data = json.loads(result.stdout)
        return data.get("findings", [])
    except json.JSONDecodeError:
        print(f"ERROR parsing scan.py output: {result.stdout[:500]}")
        return None


def build_pattern_reference_block(findings, all_patterns):
    """Build the pattern reference section for the rewriter prompt.

    Only includes patterns that appear in the findings, so the prompt
    stays focused.
    """
    referenced_ids = set(f["pattern_id"] for f in findings)
    blocks = []
    pattern_lookup = {p["id"]: p for p in all_patterns["patterns"]}

    for pid in sorted(referenced_ids):
        p = pattern_lookup.get(pid)
        if not p:
            continue
        block = []
        block.append(f"### Pattern: {p['name']} (id: {p['id']})")
        block.append(f"**Severity:** {p['severity']}")
        block.append(f"**Category:** {p['category']}")
        block.append("")
        block.append(f"**Description:** {p['description'].strip()}")
        block.append("")
        block.append(f"**Fix strategy:** {p['fix_strategy'].strip()}")
        block.append("")
        if p.get("examples"):
            block.append("**Examples:**")
            for ex in p["examples"]:
                block.append(f"- BAD:  {ex['bad']}")
                block.append(f"  GOOD: {ex['good']}")
            block.append("")
        blocks.append("\n".join(block))

    return "\n---\n\n".join(blocks)


def build_findings_block(findings):
    """Build the findings list for the rewriter prompt."""
    if not findings:
        return "No findings."
    lines = []
    for i, f in enumerate(findings, start=1):
        lines.append(f"#### Finding {i}")
        lines.append(f"- **Line:** {f['line']}")
        lines.append(f"- **Pattern:** {f['pattern_name']} (id: `{f['pattern_id']}`)")
        lines.append(f"- **Severity:** {f['severity']}")
        lines.append(f"- **Matched text:** `{f['matched_text']}`")
        lines.append(f"- **Context:** `{f['context']}`")
        lines.append("")
    return "\n".join(lines)


def build_rewriter_prompt(file_path, findings, all_patterns):
    """Fill in the prompt template."""
    template = PROMPT_TEMPLATE_FILE.read_text()
    pattern_reference = build_pattern_reference_block(findings, all_patterns)
    findings_block = build_findings_block(findings)

    # The template starts with documentation; pull only the prompt section
    # marked by '## PROMPT TEMPLATE'
    if "## PROMPT TEMPLATE" in template:
        template = template.split("## PROMPT TEMPLATE", 1)[1]
        # Strip leading separators
        template = template.lstrip("\n-").lstrip()

    return (
        template
        .replace("{FILE_PATH}", str(file_path))
        .replace("{FINDINGS_BLOCK}", findings_block)
        .replace("{PATTERN_REFERENCE_BLOCK}", pattern_reference)
    )


def emit_prompt(file_path, all_patterns):
    """Scan a file, build the rewriter prompt, print to stdout."""
    findings = run_scan(file_path)
    if findings is None:
        return 2
    if not findings:
        print(f"[CLEAN] {file_path} has no AI tells. No rewriter needed.")
        return 0

    prompt = build_rewriter_prompt(file_path, findings, all_patterns)
    print(prompt)
    return 0


def check_mode(target):
    """Just scan, no rewrite. Returns exit code 0 if clean, 1 if dirty."""
    cmd = [sys.executable, str(SCRIPT_DIR / "scan.py")]
    if target == "--all":
        cmd.append("--all")
    else:
        cmd.append(target)
    cmd.append("--exit-on-fail")
    return subprocess.call(cmd)


def list_dirty_files(target):
    """Return list of files with critical/high findings."""
    cmd = [sys.executable, str(SCRIPT_DIR / "scan.py")]
    if target == "--all":
        cmd.append("--all")
    else:
        cmd.append(target)
    cmd.append("--json")
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        files = set()
        for f in data.get("findings", []):
            if f["severity"] in ("critical", "high"):
                files.add(f["file"])
        return sorted(files)
    except (json.JSONDecodeError, KeyError):
        return []


def main():
    parser = argparse.ArgumentParser(
        description="AI Tells Pipeline Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("file", nargs="?", help="File to process")
    parser.add_argument("--all", action="store_true", help="Process all routine pages")
    parser.add_argument("--build-prompt", metavar="FILE", help="Just emit the rewriter prompt for a file (no loop)")
    parser.add_argument("--check", action="store_true", help="Scan only, exit 1 if dirty (CI mode)")
    parser.add_argument("--list-dirty", action="store_true", help="List files that need rewriting and exit")
    args = parser.parse_args()

    all_patterns = load_patterns()

    if args.check:
        target = args.file if args.file else "--all"
        sys.exit(check_mode(target))

    if args.list_dirty:
        target = args.file if args.file else "--all"
        files = list_dirty_files(target)
        if files:
            print("Files with AI tells (critical/high severity):")
            for f in files:
                rel = os.path.relpath(f, REPO_ROOT)
                print(f"  {rel}")
            sys.exit(1)
        else:
            print("[CLEAN] No files have critical/high AI tells.")
            sys.exit(0)

    if args.build_prompt:
        sys.exit(emit_prompt(args.build_prompt, all_patterns))

    # Default mode: take the first dirty file and emit a prompt for it
    if args.all or not args.file:
        dirty = list_dirty_files("--all")
        if not dirty:
            print("[CLEAN] All files are clean. Nothing to rewrite.")
            sys.exit(0)
        print(f"\nFound {len(dirty)} dirty file(s):")
        for f in dirty:
            print(f"  - {os.path.relpath(f, REPO_ROOT)}")
        print(f"\nEmitting rewriter prompt for the first dirty file:")
        print(f"  {os.path.relpath(dirty[0], REPO_ROOT)}")
        print()
        print("=" * 70)
        print()
        sys.exit(emit_prompt(dirty[0], all_patterns))
    else:
        sys.exit(emit_prompt(args.file, all_patterns))


if __name__ == "__main__":
    main()
