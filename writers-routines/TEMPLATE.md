# Writer Routine Page Template

This document defines the format and quality bar for every page in the Writers' Routines cluster. Every new routine page must follow this exact structure and pass every check before being committed.

## Page Structure

### Required sections, in order:

1. **Hook paragraph (1-2 paragraphs)**
   - Position the routine in cultural context.
   - Reframe the myth or correct a common misreading.
   - Tell the reader why this writer is worth studying.

2. **Profile card** (visual callout)
   - "PROFILE" label with gold rule above
   - Six fields, in this exact order:
     - Wake Time
     - Writing Location
     - Daily Output
     - Tools
     - Famous Ritual
     - Books Written This Way
   - Each field is concrete, sourced, and specific.

3. **Four deep-dive essay sections**
   - Each one explores one principle of the routine.
   - Real analytical prose, not bullet dumps.
   - Connect the routine to the prose it produced when possible.
   - Each section needs at least one specific, verifiable fact.

4. **One pull quote** (placed mid-essay, not at the start or end)
   - Use a real quote from the writer if possible.
   - Visual: italic Playfair Display, gold rules above and below.

5. **Sources section**
   - Minimum 3 real, citable sources.
   - Real interview names, biography titles, publication years.

6. **What You Can Steal section**
   - 4-5 actionable takeaways.
   - Bold lead-ins, written as conclusions.
   - Do NOT pivot ("Not X. Y."). Use direct statements.

7. **More Routines section**
   - 2 cross-links to other writer routines.

8. **Standard CTA + footer**
   - Same as the rest of the site.

## Word Count

- Hub: 2,500-3,500 words
- Individual writer pages: 1,800-2,500 words
- Each essay section: 3-5 paragraphs

## Voice Rules

This is the most important section. Every page must read like a working novelist wrote it, not like AI generated it.

### BANNED Patterns

These are immediate fails. If any of these appear in a draft, rewrite before committing.

1. **Pivot constructions** ("Not X. It's Y." family)
   - "It wasn't X. It was Y."
   - "She wasn't doing X. She was doing Y."
   - "He didn't X because Z. He X'd because W."
   - "Not X. Something Y-er."
   - "X, yes. But also Y."
   - These are AI's most overused construction. Use a direct statement instead.

2. **Triplet structures**
   - Three short parallel sentences ("She turned. Stopped. Stared.")
   - Three short parallel fragments ("No mercy. No hesitation. No regret.")
   - Three "He didn't X. He didn't Y. He didn't Z."
   - Three rhetorical questions in a row.
   - Cut to two, or break the parallel structure.

3. **Em-dashes**
   - Banned entirely. Use commas, periods, or rewrite.

4. **AI word tells**
   - Banned: palpable, visceral, resonated, reverberated, tapestry, labyrinth, kaleidoscope, unfurled, nestled, etched (non-physical), shattered (non-physical), fractured (non-physical), navigated (non-physical), profound, primal, fierce (describing women), unwavering, relentless
   - Banned intensifiers: utterly, absolutely, completely, entirely, wholly, fundamentally, inherently, decidedly, unmistakably, undeniably
   - Banned academic connectors: moreover, furthermore, indeed, nevertheless, nonetheless, subsequently, hence, thus, thereby, wherein

5. **Body language clichés**
   - "A shiver ran down her spine"
   - "Let out a breath he didn't know he was holding"
   - "Eyes that held [quality]"
   - "Jaw clenched"
   - "Heart hammering"
   - These don't apply much to nonfiction routine pages, but watch for them anyway.

6. **Triple-beat rhetorical patterns**
   - "Clear, concise, and compelling"
   - "Smart, resourceful, and dangerous"
   - Cut to two adjectives or rewrite.

7. **Throat-clearing openers**
   - "Here's the thing"
   - "The reality is"
   - "Look,"
   - "But here's what most people miss"
   - Just say the thing.

### REQUIRED Patterns

1. **Vary sentence length deliberately.** Long sentence, short sentence, mid-length. Never let three consecutive sentences have similar lengths.

2. **Vary sentence openings.** Don't start three sentences in a row with "She [verbed]" or "He [verbed]." Mix in prepositional phrases, subordinate clauses, fragments.

3. **Be opinionated.** Take a position. The voice should sound like a working novelist with strong views, not a neutral content blog.

4. **Use contractions naturally.** "Wasn't" not "was not." "It's" not "it is." Real people contract.

5. **Reference specific facts.** Year, source, page number when possible. Generality is a tell.

6. **Connect routine to craft.** When possible, show how the routine shaped the prose. Hemingway's standing desk → short sentences. Morrison's kitchen → domestic novels.

## The Anti-AI Scan (Required)

The anti-AI scan is now automated via the AI Tells Pipeline at `/scripts/ai-tells-pipeline/`. The pipeline reads from a single YAML pattern library and runs three layers: deterministic regex scanner, structured rewriter prompt builder, and constrained Sonnet rewriter agent.

### Workflow when building a new routine page

1. Draft the page using the rules above (Layer 1: prevention).
2. Save the file.
3. Run the scanner:
   ```
   python3 scripts/ai-tells-pipeline/scan.py writers-routines/[slug]/index.html
   ```
4. If clean, you're done.
5. If dirty, build the rewriter prompt:
   ```
   python3 scripts/ai-tells-pipeline/orchestrate.py --build-prompt writers-routines/[slug]/index.html
   ```
6. Pass the printed prompt to a Sonnet rewriter agent (`subagent_type: general-purpose`, `model: sonnet`). The agent rewrites only the flagged sentences.
7. Re-run the scanner. Repeat until clean (max 3 iterations).
8. If still dirty after 3 iterations, escalate to manual review.

### Sitewide check before commit

```
python3 scripts/ai-tells-pipeline/orchestrate.py --check --all
```

Exits 0 if clean, 1 if any critical/high findings exist. Wire this into git pre-commit if desired.

### Adding a new pattern

When you catch a new AI tell the scanner missed, add it to `scripts/ai-tells-pipeline/patterns.yaml` with a regex, severity, fix strategy, and at least one before/after example. Add a fixture to `scripts/ai-tells-pipeline/tests/fixtures.json`. Run `python3 tests/test_patterns.py` to validate. The pattern library is git-versioned, so changes are auditable and reversible.

The Hemingway and Morrison pages are the gold standard. New pages should match their voice and structure exactly.

## Reference Pages

The two existing pages are the canonical examples. Read them before building any new routine page:

- `/writers-routines/ernest-hemingway/index.html`
- `/writers-routines/toni-morrison/index.html`

Match their HTML structure, CSS classes, and prose style.

## Schema Requirements

Every page needs:
- Article schema (JSON-LD) with author Kia Orion
- BreadcrumbList schema (Home > Writers' Routines > [Author Name])
- Canonical URL
- Open Graph and Twitter Card meta tags

## Deliverables for Each New Page

When building a new writer routine page, create:

1. The HTML file at `/writers-routines/[author-slug]/index.html`
2. Update the hub page (`/writers-routines/index.html`) to add a card for the new author
3. Update sitemap.xml or sitemap-posts.xml with the new URL
4. The page must pass all anti-AI scans before commit
