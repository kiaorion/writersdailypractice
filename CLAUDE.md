# Website Design Recreation

## Workflow

When the user provides a reference image (screenshot) and optionally some CSS classes or style notes:

1. **Generate** a single `index.html` file using Tailwind CSS (via CDN). Include all content inline — no external files unless requested.
2. **Screenshot** the rendered page using Puppeteer (`npx puppeteer screenshot index.html --fullpage` or equivalent). If the page has distinct sections, capture those individually too.
3. **Compare** your screenshot against the reference image. Check for mismatches in:
   - Spacing and padding (measure in px)
   - Font sizes, weights, and line heights
   - Colors (exact hex values)
   - Alignment and positioning
   - Border radii, shadows, and effects
   - Responsive behavior
   - Image/icon sizing and placement
4. **Fix** every mismatch found. Edit the HTML/Tailwind code.
5. **Re-screenshot** and compare again.
6. **Repeat** steps 3–5 until the result is within ~2–3px of the reference everywhere.

Do NOT stop after one pass. Always do at least 2 comparison rounds. Only stop when the user says so or when no visible differences remain.



## Design Rules

- Do not add features, sections, or content not present in the reference image
- Match the reference exactly — do not "improve" the design
- If the user provides CSS classes or style tokens, use them verbatim
- Keep code clean but don't over-abstract — inline Tailwind classes are fine
- When comparing screenshots, be specific about what's wrong (e.g., "heading is 32px but reference shows ~24px", "gap between cards is 16px but should be 24px")



## Technical Defaults

- Use Tailwind CSS via CDN (`<script src="https://cdn.tailwindcss.com"></script>`)
- Use placeholder images from `https://placehold.co/` when source images aren't provided
- Mobile-first responsive design
- Single `index.html` file unless the user requests otherwise



## Lab Notes (writersdailypractice.com)

Lessons from working on the live site. Read before editing it.

- **The live site does NOT load Tailwind from the CDN**, whatever the defaults above say. It ships a pre-compiled `/css/style.css` that only contains classes present at build time, so a new utility class silently does nothing. Grep `css/style.css` before using one, or style inline. The `.article-body a` rule will turn any button inside an article into blue underlined text unless it has inline styles.
- **Every book link carries `?p=<slot>`** (nav, inline, mid, bottom, body, archive, home, bookpage). Plausible's automatic outbound-link goal records the href, so this is how placement gets measured. Keep the tag on any new CTA. Amazon ignores the parameter.
- **After any deploy, push changed pages to Bing:** `python3 scripts/indexnow.py --changed <previous-commit>`. Bing-powered engines are roughly half the search traffic and there is no Bing Webmaster Tools account; the key file at the repo root is what makes IndexNow work. Don't delete it.
- **When removing a retired offer, search for the product, not one phrase.** The August cleanup searched for "free Field Guide" and left 237 email promises behind ("delivered every morning", "your inbox", "subscribers", "sample from your daily email"). Search for the mechanism (email, inbox, subscribe, deliver, free) and check `<head>` too: titles and meta descriptions carried the same promise into search results.
- **Insert blocks between cards, never inside them.** On the archive hub each author card is an `<a>`; inserting before its `<h3>` nested one link inside another. Insert before the card's opening `<a>` and give the block `grid-column:1/-1`.
- **Verify before claiming something is missing or wrong.** Blocked crawlers, rate limits, paywalls and partial pages (the Paris Review shows only part of an interview) look exactly like absence. Run a control that should succeed first.
- **`scripts/gen_subpage.py` drifts from the live pages.** Diff its output against a live page before generating anything.
