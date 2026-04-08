# AI Tells Pipeline

A deterministic, layered system for catching and removing AI writing tells from content on writersdailypractice.com.

## What it does

The pipeline catches the patterns that signal AI-generated prose (pivot constructions like "X wasn't Y. It was Z.", em-dashes, AI word tells like "palpable" and "profound," throat-clearing openers like "Here's the thing"), and produces structured rewrite prompts that a constrained Sonnet rewriter agent can execute to fix them.

## Why it exists

When agents draft long-form content (like writer routine pages), they consistently produce AI tells even when explicitly told not to. Self-reporting is unreliable. The fix is mechanical verification: regex catches what regex can catch, and a constrained rewriter handles only the flagged sentences with no creative latitude. The drafting agent never sees the verification layer.

## File layout

```
ai-tells-pipeline/
├── README.md                       (this file)
├── patterns.yaml                   (single source of truth for all patterns)
├── scan.py                         (regex scanner, reads patterns.yaml)
├── orchestrate.py                  (loop wrapper, builds rewriter prompts)
├── rewriter_prompt_template.md     (template for the rewriter agent)
├── tests/
│   ├── test_patterns.py            (test runner)
│   └── fixtures.json               (should-match and should-not-match cases)
└── needs-manual-review/            (where files go after max iterations)
```

## Quick reference

### Scan a single file
```bash
python3 scan.py /path/to/file.html
```

### Scan all routine pages
```bash
python3 scan.py --all
```

### List files that need rewriting
```bash
python3 orchestrate.py --list-dirty
```

### Emit a rewriter prompt for a dirty file
```bash
python3 orchestrate.py --build-prompt /path/to/dirty-file.html
```

This prints a complete prompt to stdout. You feed that prompt to a constrained Sonnet agent (via Claude Code's Agent tool with `model: sonnet`). The agent rewrites only the flagged sentences and saves the file.

### Re-scan after rewriting
```bash
python3 scan.py /path/to/file.html
```

### Run the test suite
```bash
python3 tests/test_patterns.py
```

### CI / pre-commit check
```bash
python3 orchestrate.py --check --all
# Exit 0 if clean, exit 1 if any critical/high findings
```

## How it works

### Layer 1: Drafting prevention (in TEMPLATE.md)

The writer routine template includes the banned patterns and reverse examples. The drafting agent reads this before writing. This catches roughly 60% of AI tells before they're written.

### Layer 2: Regex scanner (scan.py + patterns.yaml)

After drafting, the scanner runs against the file. It reads patterns.yaml and applies each compiled regex line by line. Outputs structured findings (file, line, pattern id, severity, matched text, context). Deterministic, fast, free.

### Layer 3: Constrained rewriter (rewriter_prompt_template.md + orchestrate.py)

If the scanner finds anything, the orchestrator builds a structured prompt that includes:
- The exact file to edit
- The specific findings (line number, pattern id, matched text, context)
- The pattern reference for only the patterns that appeared (description, fix strategy, before/after examples)

This prompt goes to a Sonnet rewriter agent whose only job is to rewrite the flagged sentences. The agent has no creative latitude. It cannot draft new content. It cannot decide whether the pattern is "really" a problem.

### Layer 4: Test suite (tests/test_patterns.py + tests/fixtures.json)

Runs three checks:
1. Each pattern's own example.bad triggers its regex
2. Every should_match fixture triggers the expected pattern
3. No should_not_match fixture triggers any pattern (false positive check)

Run after any change to patterns.yaml. If any test fails, you've introduced a regression.

## Adding a new pattern

When you catch a new AI tell that the scanner missed:

1. Add the pattern to `patterns.yaml`. Include `id`, `name`, `category`, `regex`, `severity`, `description`, `fix_strategy`, and at least one before/after example.
2. Add a `should_match` fixture to `tests/fixtures.json` with text that demonstrates the pattern.
3. If your new regex might false-positive on legitimate prose, add a `should_not_match` fixture demonstrating the legitimate case.
4. Run `python3 tests/test_patterns.py`. If anything fails, fix the regex until all tests pass.
5. Run `python3 scan.py --all` to see if the new pattern catches anything in existing content. Fix any real findings.
6. Commit `patterns.yaml` and `fixtures.json` together so the test fixtures stay in sync.

The pattern library is git-versioned, so you can roll back any change that causes problems.

## Workflow integration

### When drafting a new routine page

1. Build the page using the writers-routines/TEMPLATE.md template (Layer 1 prevention).
2. Save the file.
3. Run `python3 scan.py /path/to/new-page.html`.
4. If clean, you're done.
5. If dirty, run `python3 orchestrate.py --build-prompt /path/to/new-page.html`.
6. Pass the printed prompt to a Sonnet rewriter agent.
7. After the agent finishes, re-run scan.py.
8. Repeat steps 5-7 if needed (max 3 iterations).
9. If still dirty after 3 iterations, the file goes to `needs-manual-review/` for human attention.

### When committing

Add this to a pre-commit hook or CI:
```bash
python3 scripts/ai-tells-pipeline/orchestrate.py --check --all
```
The commit fails if any critical/high findings exist in the routine pages.

## Cost notes

- Scanner: free (pure Python, no LLM)
- Tests: free
- Rewriter: Sonnet, ~5-10K tokens per dirty file (only flagged sentences, not the whole page)
- Drafting agent: Opus, unchanged (~30K tokens per page)

Total per page: roughly the same as today, but with manual rewrite work eliminated.

## Known limits

- Regex can't catch semantic pivots (e.g., "X, but actually Y" where the contrast is implied rather than structural)
- Triplet detection is not yet implemented (planned for next version)
- The rewriter is a separate agent invocation, so the drafting and rewriting steps are decoupled. This is intentional (different cognitive jobs, different prompts) but means the workflow has two manual steps instead of one
- Pattern discovery is currently manual (you add patterns when you catch them). Automated discovery via human-corpus comparison is planned for the next version

## Future enhancements (Layers 5-13)

The current implementation is the essential 6-layer version. The full 13-layer system (per the design discussion) would add:

- Layer 5: Metrics dashboard tracking pattern frequency over time
- Layer 6: Pattern discovery via comparison to a human prose corpus
- Layer 7: Calibration buckets (auto-fix vs flag vs escalate)
- Layer 10: Second-pass LLM scanner for semantic patterns regex misses
- Layer 11: Token budget guard
- Layer 12: LLM scanner validation period
- Layer 13: GitHub Action for autonomous operation

These will be added if the essential version proves valuable in practice.
