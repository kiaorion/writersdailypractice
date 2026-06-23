#!/usr/bin/env node
/**
 * convertkit-stats.mjs
 *
 * Pulls email-list growth numbers from ConvertKit / Kit for the WDC weekly report.
 * Reads the API secret from ~/.claude/api-keys.md (never from the repo).
 *
 * Outputs:
 *   - total subscribers (active)
 *   - net-new subscribers in the last 7 and 28 days
 *   - signups attributed to the routine-page form (9155962) in the last 7 and 28 days
 *
 * Usage:
 *   node scripts/convertkit-stats.mjs
 *   node scripts/convertkit-stats.mjs --json     # machine-readable output
 *
 * Notes:
 *   - Uses ConvertKit API v3 (api_secret auth). v3 is still live and is the
 *     simplest credential to obtain (Settings > Advanced/Developer > API Secret).
 *   - The default capture form is 9155962 (embedded on the routine pages).
 */

import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const FORM_ID = "9155962";
const KEYS_PATH = join(homedir(), ".claude", "api-keys.md");
const API = "https://api.convertkit.com/v3";
const asJson = process.argv.includes("--json");

function loadSecret() {
  let text;
  try {
    text = readFileSync(KEYS_PATH, "utf8");
  } catch {
    fail(`Could not read ${KEYS_PATH}. Add the ConvertKit block first.`);
  }
  const m = text.match(/CONVERTKIT_API_SECRET\s*[=:]\s*([^\s#]+)/i);
  if (!m) {
    fail(
      "CONVERTKIT_API_SECRET not found in api-keys.md.\n" +
        "Add:\n  ## ConvertKit (Kit)\n  CONVERTKIT_API_SECRET=your_secret_here"
    );
  }
  return m[1].trim();
}

function fail(msg) {
  console.error(`\n[convertkit-stats] ${msg}\n`);
  process.exit(1);
}

function daysAgoISO(n) {
  // Date math without Date.now-style helpers being an issue at runtime (this is a plain node script).
  const d = new Date(Date.now() - n * 24 * 60 * 60 * 1000);
  return d.toISOString().slice(0, 10);
}

async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    fail(`API ${res.status} ${res.statusText} for ${url.replace(/api_secret=[^&]+/, "api_secret=***")}\n${body.slice(0, 300)}`);
  }
  return res.json();
}

/** Total active subscriber count (uses pagination meta, doesn't page through everyone). */
async function totalSubscribers(secret) {
  const data = await getJSON(`${API}/subscribers?api_secret=${secret}&per_page=1`);
  return data.total_subscribers ?? null;
}

/** Net-new subscribers created within [from, to] using the created-date filter. */
async function newSubscribers(secret, fromISO) {
  const data = await getJSON(
    `${API}/subscribers?api_secret=${secret}&from=${fromISO}&per_page=1`
  );
  return data.total_subscribers ?? null;
}

/** Signups to a specific form within a window (pages through subscriptions). */
async function formSignups(secret, fromISO) {
  const from = new Date(fromISO + "T00:00:00Z").getTime();
  let page = 1;
  let count = 0;
  let totalPages = 1;
  do {
    const data = await getJSON(
      `${API}/forms/${FORM_ID}/subscriptions?api_secret=${secret}&sort_order=desc&page=${page}`
    );
    totalPages = data.total_pages ?? 1;
    const subs = data.subscriptions ?? [];
    let stop = false;
    for (const s of subs) {
      const t = new Date(s.created_at).getTime();
      if (t >= from) count++;
      else {
        stop = true; // sorted desc, everything past here is older
        break;
      }
    }
    if (stop) break;
    page++;
  } while (page <= totalPages);
  return count;
}

async function main() {
  const secret = loadSecret();
  const from7 = daysAgoISO(7);
  const from28 = daysAgoISO(28);

  const [total, new7, new28, form7, form28] = await Promise.all([
    totalSubscribers(secret),
    newSubscribers(secret, from7),
    newSubscribers(secret, from28),
    formSignups(secret, from7),
    formSignups(secret, from28),
  ]);

  const out = {
    total_subscribers: total,
    new_subscribers_7d: new7,
    new_subscribers_28d: new28,
    form_signups_7d: form7,
    form_signups_28d: form28,
    form_id: FORM_ID,
    window_7d_from: from7,
    window_28d_from: from28,
  };

  if (asJson) {
    console.log(JSON.stringify(out, null, 2));
    return;
  }

  console.log("\nConvertKit / Kit — WDC list growth");
  console.log("----------------------------------");
  console.log(`Total active subscribers:      ${total ?? "n/a"}`);
  console.log(`New subscribers (last 7d):     ${new7 ?? "n/a"}`);
  console.log(`New subscribers (last 28d):    ${new28 ?? "n/a"}`);
  console.log(`Routine-form signups (7d):     ${form7} (form ${FORM_ID})`);
  console.log(`Routine-form signups (28d):    ${form28} (form ${FORM_ID})`);
  console.log("");
}

main().catch((e) => fail(e?.message || String(e)));
