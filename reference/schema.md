# Dataset schema

A dataset is a single JSON object that carries everything domain-specific. `assets/template.html`
is a fixed engine that renders any valid dataset; you never edit the template. `scripts/build.py`
validates a dataset and splices it into the template to produce the final self-contained HTML.

**There is no `flow` block.** This tool has no decision flowchart, so the **blueprint is the single
source of truth**: every column carries its own header,
question, input factors, requirement ids, and outcomes.

Top-level keys: `meta`, `tiers`, `requirements`, `blueprint`, and optional `outcomeKinds`.

```jsonc
{
  "meta": { ... },
  "tiers": [ ... ],
  "requirements": [ ... ],
  "blueprint": { ... },
  "outcomeKinds": { ... }   // optional
}
```

## meta

```jsonc
{
  "title": "MD SNAP & Medicaid — Verification at Initial Application — Service Blueprint",
  "subtitle": "Verification at initial certification · actors: applicant / caseworker / system · federal regulation controls",
  "authorityLabel": "Multiple policies",   // long form, used in the ⚖ callout & legend
  "authorityBadge": "Multiple policies",   // short word shown on the ⚖ badge and the "only ___ links" filter
  "sources": [                              // OPTIONAL — populates the "View sources" drawer
    { "label": "COMAR 07.03.17 — …", "url": "https://…", "note": "User-provided · Maryland SNAP/FSP regulation" }
  ],
  "research": {                             // REQUIRED — the Step 0 research-gate record (see reference/research-packet.md)
    "packet": "md-snap-verification-research-packet.md",  // packet file name, kept beside this dataset
    "completed": "2026-07-27",              // packet manifest `completed` (YYYY-MM-DD)
    "currencyCheck": "2026-07-27",          // packet manifest `currency_check` (YYYY-MM-DD)
    "verifyFlags": 3                        // packet manifest `verify_flags` (open [verify] count)
  }
}
```

`research` is **required**: `build.py` fails validation without it — no completed Research Packet,
no build. `"packet": "legacy:pre-protocol"` is accepted (with a loud warning, other fields then
optional) only for datasets that predate the research gate; never write it in new work.

`sources` is an ordered array of `{label, url, note}`. List user-provided link(s) first, then any
supporting authorities you fetched. Use `authorityBadge`/`authorityLabel` = `"preemption"` for a
federal-vs-state supremacy story, or leave the default `"Multiple policies"` for a single-sovereign
hierarchy.

## tiers

Legal-authority levels for this domain, highest authority first. `rank` drives sorting and the
"dominant tier" color; `color` themes badges, chips, and card borders.

```jsonc
{
  "key": "federal_reg",                    // lowercase letters/digits/underscores only (used in CSS class names)
  "label": "Federal regulation (7 CFR / 42 CFR)", // shown as the Type pill (its parenthetical is trimmed off in the UI)
  "rank": 1,                                // 1 = highest authority; lower rank wins "dominant tier"
  "color": "#1e3a8a"                        // #rrggbb — the Type pill / chip color
}
```

Typical palette: `#1e3a8a` deep blue · `#6d28d9` purple · `#047857` green · `#0f766e` teal.

## requirements

Each is one implementable rule traced to a single citation. **Two fields are new** versus the
Explorer: `actor` and `nature`.

```jsonc
{
  "id": "SNAP-04",                          // short stable id, unique
  "topic": "SNAP — Questionable information",// UNIQUE per requirement — doubles as the chip label ("<Area> — " prefix is trimmed) and side-panel title; also powers the topic display + filter
  "tier": "state_reg",                       // must match a tiers[].key
  "actor": "caseworker",                     // NEW — which actor lane carries this rule (matches blueprint.actors[].key)
  "nature": "operational",                   // NEW — "policy" (default) or "operational"; operational renders 🛠 dashed
  "citation": "COMAR 07.03.17.20G",          // the single controlling citation
  "citationUrl": "https://regs.maryland.gov/us/md/exec/comar/07.03.17", // OR null — makes the citation a clickable link in the side panel; use the same source-doc URL from meta.sources
  "statement": "The system must flag a factor as 'questionable' only when …", // plain-language, implementation-facing
  "quote": "A factor of eligibility is questionable when …",  // VERBATIM source text — a string; see quote rules below for the rare multi-quote array form
  "authority": {                             // OR null — present only when a higher authority controls this rule
    "higher": "7 CFR 273.2(f)(1)",
    "higherUrl": "https://www.ecfr.gov/current/title-7/section-273.2", // OR null — links the higher citation to its source doc
    "lower":  "COMAR 07.03.17.20C",
    "lowerUrl": "https://regs.maryland.gov/us/md/exec/comar/07.03.17", // OR null — links the lower citation to its source doc
    "higherRef": null,                       // OR a requirement id — internal cross-link, used only when no higherUrl
    "lowerRef":  null,                        // OR a requirement id — internal cross-link, used only when no lowerUrl
    "controls": "federal",                    // which side controls on conflict
    "note": "Federal rules set the list; COMAR adopts it for Maryland."
  },
  "forms": ["Notice of Required Verification"], // OR null — process artifacts the requirement depends on
  "gap": "'Inconsistent' is not quantified — left to caseworker judgment."  // OR null — an AI-suggested ambiguity/risk
}
```

Rules of integrity:
- `topic` must be **unique across all requirements** — it is the chip label and side-panel title, so
  duplicates render as identical chips. Use `"<Area> — <Unique name>"`; the engine trims the
  `"<Area> — "` prefix on the chip, keeping labels short while preserving area grouping elsewhere.
- `quote` must be **verbatim**; paraphrase belongs in `statement`. It is normally a **single
  string**. In the rare case that one chip legitimately merges rules from more than one program
  (e.g. a shared cross-program requirement in a multi-program blueprint), `quote` may instead be an
  **array** of strings or `{ "quote": "…", "citation": "…" }` objects, so each program keeps its own
  verbatim text and citation label — each renders as its own blockquote in the side panel. This is
  an edge case: default to one quote per requirement, and prefer splitting into per-program
  requirements over merging.
- Never invent or alter a `citation`. If unsure, leave the requirement out or flag it in `gap`.
- `citationUrl` is optional. When set, the side panel renders the citation as a link that opens the
  source document in a new tab. Reuse the exact URL from `meta.sources` for that citation's source;
  leave it `null` when you don't have a reliable link (never guess a URL).
- `actor` **should** match one of `blueprint.actors[].key`. If it's missing or unknown, the engine
  drops the requirement into the **last** actor lane and `build.py` warns — so set it deliberately.
- `nature` defaults to `"policy"`. Use `"operational"` for agency practice / caseworker judgment
  that is not strict statutory policy (e.g. fault analysis, questionable-info calls, case-by-case
  exceptions). This is the mechanism that keeps operational workflow visually distinct from policy.
- Whenever `authority` is present, link its `higher`/`lower` citations to sources: set `higherUrl`
  and `lowerUrl` to the matching URL from `meta.sources` (add a supporting-authority source if the
  cited reg isn't already listed). Resolution order per side: `higherUrl`/`lowerUrl` → else
  `higherRef`/`lowerRef` (internal cross-link to another requirement) → else plain bold text.
  Reliable-or-nothing; never guess a URL.

## blueprint

The blueprint is self-contained. Rows: the claimant question (+ input factors), one lane per
`actors[]` entry, and the outcome. Columns: one per step, in reading order.

```jsonc
{
  "intro": "Verification at initial application as a service blueprint …",
  "claimLane": "Applicant sees / is asked",   // optional; sensible default exists
  "outcomeLane": "Outcome",                    // optional
  "actors": [                                  // NEW — the responsibility lanes (choose what fits the policy); { key, label } each
    { "key": "applicant",  "label": "Applicant action" },
    { "key": "caseworker", "label": "Caseworker (manual)" },
    { "key": "system",     "label": "System (automated)" }
  ],
  "columns": [
    {
      "id": "S1",                              // stable unique id
      "title": "Mandatory verification before certification",  // column header (the step is auto-labeled "Step 1", "Step 2"… by position within its table)
      "group": "SNAP application",             // OPTIONAL — consecutive same-group columns render as a separate stacked "alternative path" table
      "q": "Can you document identity, income, residency, SSN, and resources?",  // the claimant-facing question
      "inputs": ["Identity","Gross income","Residency","SSN","Included resources"],  // OPTIONAL input factors, shown in the dedicated Inputs swimlane
      "reqs": ["SNAP-03","SNAP-01","SNAP-02"], // requirement ids tested at this step; distributed into actor lanes by each req's actor
      "out": [                                 // branch outcomes (read-only result labels)
        { "t": "Verified → certify", "kind": "good" },
        { "t": "Missing / questionable → request", "kind": "proc" }
      ]
    }
  ],
  "crosscut": {                                // OPTIONAL — rules that apply across every step
    "label": "Applies across every step: confidentiality & data handling",
    "reqs": ["CONF-01","CONF-02"]
  }
}
```

- Each column's `reqs` are distributed into the actor lanes automatically: a chip appears in
  column *C*, lane *A* when the requirement's `actor` is *A* and its id is in `C.reqs`. A lane can
  legitimately be empty for a step.
- `out[].kind` uses the outcome kinds below; outcome pills are read-only result labels.
- `group` is optional but structural. **Consecutive columns sharing a `group` render as their own
  separate stacked table**, each with its own titled header banner marked "alternative path" — so
  parallel journeys (e.g. a SNAP path and a Medicaid path) read as distinct tables rather than one
  wide sequence. Columns with no `group` render as a single untitled table.
- There is no bottom "Outcome" summary legend and no trailing Outcome column — per-step `out`
  pills carry the outcomes.

## outcomeKinds (optional)

Override the default colors for outcome kinds. Defaults:

```jsonc
{ "good":"#065f46", "bad":"#991b1b", "partial":"#a16207", "nd":"#b45309", "na":"#475569", "proc":"#6b7280" }
```

`good` = benefit/eligibility granted · `bad` = denied/not payable · `partial` = reduced benefit ·
`nd` = needs determination/adjudication · `na` = not applicable / step skipped · `proc` =
continue / processing.
