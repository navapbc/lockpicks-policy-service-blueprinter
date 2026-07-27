---
name: policy-service-blueprinter
description: >
  Turn a few policy-document links (statutes, regulations, sub-regulatory manuals, agency
  operating procedures) into a claimant-side service blueprint for any government benefits or
  services use case (UI, SNAP, Medicaid, PFML, VA, and others). Produces one self-contained HTML
  tool with actor swimlanes, operational-vs-policy flags, per-step input factors, verbatim source
  quotes, authority callouts, and plain-language outcomes, in a locked house style.
  Requirements come from policy alone, never the current app, UI, or legacy system. Use when
  someone pastes statute/regulation/official-guidance links, says "map these regulations for
  [program]," or asks to turn policy into a blueprint/requirements view. If the source looks like
  a legacy system or "how it works today" docs, ask first — never blueprint
  current-implementation behavior. Every blueprint is research-gated: the
  policy-analysis-protocol skill runs first and produces the Research Packet the dataset must
  reference. A policy SME must review results.
---

# Policy Service Blueprinter (Team Edition)

This is a team-hardened build of the Policy Service Blueprinter. It produces the **same polished
output every time** from nothing but a few policy links, so people with no AI or coding background
can run it and get an identical, review-ready result. The visual design and conventions are locked
in — do not re-derive them and do not ask the user about styling.

> ⚠️ **Human review required.** This tool AI-extracts legal requirements. Every blueprint is a
> **draft for discovery and alignment** and must be reviewed by a policy subject-matter expert
> before it informs any decision, system, or communication. Say this to the user on delivery, every
> time.

## Prerequisites

- **Python 3** — to run `scripts/build.py` (standard library only; no packages to install).
- **`policy-analysis-protocol` skill (required companion)** — produces the Research Packet that
  gates every build (see Step 0). If it isn't installed, run the protocol inline to the same
  rigor: the packet contract is `reference/research-packet.md`, and the full method it points to
  ships with that skill. Either way, no packet → no dataset.
- **`policy-document-analysis` skill (recommended, not required)** — the intended companion for the
  analysis step. If it isn't installed, do the same analysis inline to the same rigor (see Step 3);
  the skill still works, it just does more of the reading itself.

## Policy is the single source of truth — extract from policy alone

**This is the first principle of the skill; it overrides any instinct to describe the system as it
exists today.** The blueprint represents **policy, and policy only**. Every requirement is extracted
from an authoritative policy document — a statute, a regulation, or official sub-regulatory policy
(an agency operating manual, a program guidance letter, an official policy memo). Nothing else
generates a requirement.

**Never derive requirements from — or organize the blueprint around — the current implementation.**
The existing application or intake form, UI screens or screenshots, a legacy system's rules /
screening logic / code / configuration, data dictionaries, vendor documentation, prior tools, or
"how it works today" are **not policy** and are **never sources of truth**. If the user provides
them, or you encounter them while researching, treat them strictly as non-authoritative context for
*scoping* — they must never become a requirement, a tier, a column, a chip, an input factor, or an
outcome, and they must never shape how the blueprint is structured.

Organize the blueprint around the **policy determination itself** — its legal requirement areas
(e.g., valid claim, monetary eligibility, separation, ability & availability) — **never** around the
sections of a form or the screens of a system. Frame each requirement as *what the law requires and
the constraint on it* (mandatory vs. permissive, federal floor vs. state discretion, controlling
authority, conditions, ambiguities). Where a policy document delegates a detail to agency discretion,
capture that **as a constraint** in `gap`/`authority` — do **not** import the implementation that
filled the gap.

Why this matters: the whole value of the blueprint is a clean, standalone statement of what policy
requires. Mixing in current-implementation or legacy-system behavior makes people mistake "how it's
done" for "what's required" — the exact confusion this tool exists to remove.

## Facts are fetch-only; interpretation is labeled

Two epistemic rules govern everything the skill writes — in the dataset and in conversation:

**1. Facts: fetch-or-don't-assert.** Every factual legal claim — what a rule requires, who it
covers, any number, deadline, threshold, or dollar figure — must trace to source text **fetched
this session**. Model background knowledge is never a basis for asserting a fact, no matter how
confident it feels. A citation that has been confirmed to exist but whose text was not read may be
cited *as existing* — but its contents may **not** be characterized until fetched: a description of
unread text is background knowledge wearing a citation. If a fact can't be fetched, leave the
requirement out or surface the hole in `gap` — never assert it.

**Numeric verify tally.** Figures are the highest-risk facts: they go stale, vary by state, and
look authoritative on a chip whether or not they're right. Any figure not yet confirmed against
fetched text is (a) marked "to verify" where it appears (in `gap`), and (b) added to a **running
verify tally** kept across the whole run. Report the tally on delivery, and offer **one
consolidated verification pass** against primary sources — rather than verifying piecemeal or,
worse, asserting.

**2. Interpretation: labeled, never disguised as fact.** Structural and interpretive judgments —
how to split steps, whether rules merge, what a provision is *for*, which authority likely
controls — cannot be fetched; they are the skill's reasoning, unavoidably informed by background
knowledge. Never present them as settled fact. Frame them explicitly as interpretation ("my read"),
keep them out of dataset fact fields (`statement`, `quote`), and attach a **standing offer to
corroborate** against primary text or scholarly/expert sources before the judgment is locked into
the structure. If the user asks what a recommendation rests on, answer plainly and specifically —
including where it rests on general program knowledge rather than anything read this session.

## Bundled engine — never swap it, never re-style

This skill ships its own rendering engine and build script. Always build with the **bundled** files:

- `assets/template.html` — the fixed engine with the locked house style baked in.
- `scripts/build.py` — validates a dataset and splices it into the bundled template.

Build command (from the skill directory, or with absolute paths):

```
python3 scripts/build.py <domain>.json --out <Domain>-Blueprint.html
```

Do **not** use any other template, and do **not** hand-edit the generated HTML for styling — the
locked patterns below are already in the engine. Your only job each run is to produce a correct
dataset JSON, then build.

### Locked design patterns (already in the engine — do not touch)

1. **Local-only sources render as plain text.** In the "View sources" drawer, a source with
   `"url": null` shows as bold plain text (no broken link); put the file name in `note`. Web sources
   keep a real `url` and render as a link.
2. **Crosscut bar:** light-blue (`#d9e8f6`) background, dark text, a **serif subheading** label
   (no icon, no trailing colon, not uppercase), with the requirement chip(s) inline to the right,
   wrapping in a row.
3. **Roomier outcome pills** (`padding:.4rem .75rem`) so text never touches the border.
4. **Wider columns + horizontal scroll** (label 140px, steps `minmax(250px,1fr)`, grid min-width
   forces side-scroll).

### Locked dataset conventions (set these in every dataset — identical every time)

- **USWDS tier palette**, highest authority first. Reuse these hex values; add/drop tiers to fit the
  program's sovereignty story but always pull colors from this set:
  - `federal_reg` → `#1a4480` (USWDS blue-warm-70v)
  - `state_statute` → `#54278f` (USWDS violet-70v)
  - `state_reg` → `#0c4e29` (USWDS mint-70v)
  - `agency_ops` → `#07648d` (USWDS blue-cool-60v)
- **`meta.subtitle` and `blueprint.intro` are always `""`** — the header stays clean.
- **Crosscut `label`** is a short plain phrase — no trailing colon, no explanatory sentence (the
  chip carries the meaning). e.g. `"Applies across every certification question"`.
- **Actor lanes** default to claimant / system / caseworker; adapt names to the domain if needed.
- **Every requirement gets a unique display name.** `topic` doubles as the chip label and the
  side-panel title, so **no two requirements may share the same `topic`** — duplicate topics render
  as identical, indistinguishable chips. Use the format `"<Area> — <Unique name>"` (e.g.
  `"Pension offset — 60-day rollover exemption"`): the engine drops the `"<Area> — "` prefix on the
  chip, so chip labels stay short and unique while the full name (with its area grouping) shows in
  the side panel and the All-requirements table. Check uniqueness before building.
- **`nature: "operational"`** only for a step that is *itself official agency policy* — a published
  operating manual or sub-regulatory guidance document — so it stays visually distinct (🛠) from
  statute/regulation; note the murkiness in `gap`. **This is not a back door for the current
  implementation.** A legacy system's screening logic, code tables, or matrices, and anything read
  off the live form/UI, are not policy and do not belong in the dataset at all — do not label them
  operational, just leave them out (see "Policy is the single source of truth"). Default to `policy`;
  reach for `operational` sparingly and only when a real policy document is the source.
- **Bluebook-standard citations, always with the jurisdiction qualifier.** Every `citation`,
  `authority.higher`/`lower`, and every citation you write in conversation follows Bluebook format
  and names its sovereign: "C.R.S. § 8-73-107" (never a bare "Title 8" or "§ 8-73-107"),
  "7 C.F.R. § 273.2(b)(3)", "42 U.S.C. § 503(a)(1)", "7 CCR 1101-2". A citation that could be read
  as belonging to a different sovereign's code is an error — an attorney reading "Title 8" cannot
  tell the Colorado Revised Statutes from the federal title.
- **Verbatim `quote` only; never invent a `citation`; `citationUrl` only when a reliable public URL
  exists** (else `null`, with the local file name in `meta.sources[].note`). `quote` is normally a
  single string; only when one chip legitimately merges rules from more than one program (a rare,
  multi-program edge case) may it be an array of `{quote, citation}` objects so each program keeps
  its own verbatim text — see `reference/schema.md`.
- **`meta.research` is required in every dataset** — the record of the Step 0 gate. It names the
  Research Packet file (kept beside the dataset) and carries the packet's `completed`,
  `currency_check`, and `verify_flags` values (see `reference/research-packet.md`). `build.py`
  fails without it. The `"legacy:pre-protocol"` value is for pre-gate datasets only — never new
  work.

Copy `examples/blueprint-starter.json` — it already encodes all of the above.

## Order of operations

### Step 0 — Research gate (always; auto-satisfy, never hard-block)

**No blueprint dataset is ever built without a completed Research Packet**
(`reference/research-packet.md`). The gate exists so every blueprint stands on a verified
authority set — federal framework always established, citations confirmed on official sources,
currency checked — instead of only whatever links the user happened to paste.

1. **Look for a packet:** one the user provided, one produced earlier this session, or a
   `<domain>-research-packet.md` beside where the dataset will be built.
2. **If none exists, run the `policy-analysis-protocol` skill now** (inline to the same rigor if
   it isn't installed) and produce the packet before proceeding. Do not announce a blocker — the
   gate is satisfied by *doing the research*, not by refusing. The user experience stays: paste
   links, answer the intake questions, get the tool.
3. **If a packet exists, validate it** against the completion checklist in
   `reference/research-packet.md` (manifest parses; federal layer substantive; sources carry
   confirmation dates; currency check dated; verify flags collated). An incomplete packet means
   finishing the research, not building around it.
4. Carry the packet forward: its source inventory seeds Step 2, its interaction analysis anchors
   the tiers and `authority` callouts in Steps 3–4, its verify-first list seeds the verify tally,
   and the dataset's `meta.research` block records it (see locked conventions).

Never write the `legacy:pre-protocol` escape value in a new dataset — it exists only so datasets
that predate this gate keep building honestly.

### Step 1 — Intake (ONE question, forgiving defaults)

Non-technical users will usually paste **only links**. Do not hard-stop for a long spec. Confirm you
have the documents, then ask exactly **one** scope question with a sensible default pre-selected —
and if Step 0 is running the research protocol in the same breath, fold its jurisdiction question
("federal only, or federal plus which state(s)?") into this same intake moment: one pause, two
questions maximum.

> "I'll map the **whole determination** in these documents into a service blueprint. Want me to
> narrow it to one slice (e.g. just the weekly certification decision, or just verification at
> application), or model the whole thing?"
> — Default: **model the whole determination.**

If they don't answer or say "just do it," proceed with the whole-determination default. Never block.
Record every link in `meta.sources` (mark local files with `url: null` + file name).

### Step 2 — Gather the sources (self-healing; never make the user debug)

Start from the **Research Packet's source inventory (section 9)**, not just the user's pasted
links — the packet includes the federal-layer and overlay sources the user didn't know to paste,
already confirmed against official codifiers. The user's links are a subset of the inventory, not
the ceiling. Verbatim quotes still require text fetched this session (facts are fetch-only), even
for sources the packet verified. For each source, get clean text automatically:

1. Fetch the URL (WebFetch / web_fetch).
2. **Detect a thin/JS-rendered result** — a near-empty body, a "please enable JavaScript" shell,
   only nav/boilerplate, or content that clearly lacks the policy text. Government portals like
   state admin-code sites and VA's KnowVA (M21-1) commonly return this.
3. If thin, **automatically escalate to a rendering browser** (Claude in Chrome: navigate →
   get_page_text) to read the JS-rendered page.
4. Prefer official static text (eCFR, Cornell LII, govinfo) for verbatim regulation/statute language
   when both exist.
5. Only if a source still can't be read after the browser fallback, tell the user plainly which link
   failed and ask them to paste the text or a different link — never leave them guessing.
6. **Save what you fetch.** Write each source's clean text into a `sources/` folder beside where
   the dataset will live (one file per document; user-supplied local corpus files count as already
   saved). Extract from the saved files with scripts instead of re-reading pages — it keeps the
   context lean — and it is what makes Step 5's mechanical quote verification possible: a quote
   whose source text was never saved cannot be verified. Remember WebFetch **summarizes** — for
   verbatim capture use raw-text endpoints, download-and-extract, or the rendering browser.

### Step 3 — Analyze the sources

Decompose each **policy** source into anchored, verbatim rules with conditions, precedence, and
ambiguity flags.

**Authority anchoring — ask, don't decide.** The usual posture is federal law controlling and state
law implementing. Some programs invert it: unemployment insurance, for example, is state-anchored —
the state statute supplies the operative eligibility and disqualification standards while federal
law acts as a conformity ceiling. If the sources suggest the program's controlling-authority story
may be inverted (or genuinely ambiguous), do **not** pick an anchoring yourself: tell the user what
you're seeing and ask how to anchor the tiers — state-anchored with the federal layer noted,
federal-anchored, or both layers as explicit `authority` callouts — before building the dataset.

Use the `policy-document-analysis` skill if it is installed; otherwise analyze inline holding to
the same rigor. Every requirement in the dataset must trace to a real rule in a
**policy document** with a verbatim quote — if the only thing that supports it is the current form,
a screenshot, or a legacy system's behavior, it is not a requirement and does not go in (see "Policy
is the single source of truth"). Analyze only policy; ignore non-policy artifacts except to bound
scope.

### Step 4 — Build the dataset (follow the locked conventions)

Map the analysis into the dataset per `reference/schema.md` and `reference/extraction-guide.md`,
applying the locked conventions above. Assign each requirement an `actor` and `nature`.

**Overlay completeness check.** A policy-first analysis goes deep on the program's own rules and
reliably under-collects the generally-applicable federal overlays — civil-rights/language access,
payment-method and disclosure rules, tax withholding, confidentiality, QC/audit data duties.
Before building, sweep the Research Packet's federal-framework overlays (section 2) and confirm
each is either in the dataset — usually as a **crosscut**, since these obligations are pervasive
rather than step-bound — or explicitly noted out-of-scope in a `gap`. Never let them silently
vanish.

**Default column-split rule (so density never blocks a non-expert):** no single actor cell may hold
more than 6 requirement chips. If a step would exceed that, **split it by sub-topic in reading
order** into adjacent columns (same `group` if grouped), and briefly tell the user you did so. Do not
stop to ask how to split unless the sub-topics are genuinely unclear.

### Step 5 — Build, verify, deliver

1. **Mechanically verify every quote first:** `python3 scripts/verify_quotes.py <domain>.json`
   (checks each `quote` copy-exact — whitespace/punctuation-normalized — against the text saved in
   `sources/` during Step 2). Fix every miss: a miss is a paraphrase or an unsaved source, and both
   are build blockers, not footnotes. Verification happens **here, before delivery** — never as a
   retrofitted audit after the tool has shipped.
2. `python3 scripts/build.py <domain>.json --out <Domain>-Blueprint.html`. Fix every ❌ error and
   review ⚠️ warnings.
3. Verify: embedded JSON parses; every requirement surfaces in a column or the crosscut; quotes and
   citations match the sources; actor lanes and operational flags read correctly; source links open
   (and local-only sources show as plain text); the page renders with no console errors;
   `meta.research` points to the packet, the packet sits beside the dataset, and its verify-first
   list is reflected in the verify tally you report.
4. **Report verbatim-quote coverage and the verify tally on delivery.** State plainly how many
   requirements carry machine-verified verbatim source text (the step-1 script count), and name
   anything that was left out or flagged in `gap` because its text could not be retrieved. In every
   report — and any time you say "verified" afterwards — the word means **machine-verified quote
   text and nothing more**: tiers, step order, actor lanes, and any applicability judgments are
   analyst interpretation and never ride under that word. If any source failed to yield verbatim text on the
   first pass, offer a **targeted second retrieval pass** (rendering browser, alternate official
   mirrors — eCFR, Cornell LII, govinfo, state code portals) before the user starts reviewing —
   never let the user discover coverage gaps on their own. In the same report, list the **verify
   tally** — every figure still marked "to verify" — and offer the consolidated verification pass.
5. **Deliver a known-limitations self-critique with the tool, unprompted.** A short, honest list:
   method risks (single-pass extraction, the corpus boundary from the Research Packet, unverified
   quotes), judgment calls a reviewer might contest (step order, actor lanes, merged rules), and
   currency caveats. The receiving team will critique the work anyway — arrive having done it
   first.
6. Deliver the HTML **and** repeat the human-review caveat. Keep the dataset JSON, the Research
   Packet, the `sources/` folder, and the analysis alongside it so the tool can be regenerated or
   audited.

### Step 6 — Offer the SME review walkthrough (every time)

Immediately after delivering the initial HTML, **always offer a guided review walkthrough as the
next step** — this is how the required SME review actually happens, so don't wait to be asked:

> "Want to review it together? I'll walk the blueprint one step at a time — you correct anything
> that's wrong, and I'll rebuild once at the end."

If accepted, run it like this:

1. **One step at a time, exactly as built.** For each column show the claimant question, inputs,
   outcomes, and every requirement with its id, actor lane, tier, citation, and one-line rule —
   then give your read on what's contestable (structure, actor, tier, citation, wording,
   policy-vs-operational), and let the SME direct the changes. Their read governs; yours is input.
   Frame your read per the interpretation rule above — judgment, not fact — and where it rests on
   anything not fetched this session, say so and offer to corroborate before the step is locked.
2. **Keep a running change log** and restate it as it grows, so the SME always sees the accumulated
   change set.
3. **Batch everything into one validated rebuild at the end.** All changes go into the dataset JSON
   and through `build.py` — never hand-edit the HTML, and don't rebuild mid-walk.

Two working conventions, during the walkthrough and any time after delivery:

- **Preview before commit.** For any visual or structural change to the tool, show a preview or
  mockup and get a go-ahead before applying it to the real build.
- **Read back complex direction.** When the user gives a multi-part instruction, restate it back
  in your own words and confirm before implementing.
- **Re-read before re-editing.** The dataset is a shared artifact — teammates may have reworked it
  since the last build, reusing requirement ids with new meanings. Before changing any requirement
  by id, re-read its current content; editing by remembered meaning has destroyed human-authored
  notes.

## Derived deliverables (tables, CSVs, memos)

Blueprints regularly spawn downstream artifacts — applicant data-element tables, crosswalks,
handoff memos. Three rules:

- **Ask for the team's format before generating.** If the artifact is going to policy specialists,
  ask for a sample of the format they already work in (or reuse one from earlier in the session).
  Discovering the preferred format after delivery costs a full rebuild cycle.
- **Every row carries traceability:** the requirement id(s)/topic it traces to and the citation, so
  a reviewer can walk cell → requirement card → verified quote → source.
- **Label provenance and judgment in reviewer language.** Flag non-primary rows explicitly (e.g.
  "Present in guidance document, not in policy docs"), and keep analyst-judgment columns
  (per-persona Yes/No, applicability calls) visibly distinct from machine-verified facts.

## Reference files (in this package)

- `assets/template.html` — the locked rendering engine.
- `scripts/build.py` — validate + build.
- `scripts/verify_quotes.py` — mechanical quote check: every dataset `quote` must be found
  copy-exact (whitespace/punctuation-normalized) in the text saved under `sources/`. Run it in
  Step 5 before every delivery.
- `scripts/test.py` — regression check; validates and fully builds every dataset in `examples/`.
  Run `python3 scripts/test.py` before packaging or sharing — it exits non-zero if any example
  breaks, so it's safe to wire into CI.
- `reference/schema.md` — dataset schema.
- `reference/extraction-guide.md` — analysis → dataset mapping.
- `reference/research-packet.md` — the Research Packet contract (canonical copy): what the
  `policy-analysis-protocol` skill must hand over, the completion checklist Step 0 validates, and
  the `meta.research` dataset block.
- `examples/blueprint-starter.json` — dataset skeleton with all conventions preset (copy this).
- `examples/de-ui-initial-claim.json` — a complete worked example (Delaware UI initial-claim
  application): 54 requirements across 15 steps, four authority tiers, three actor lanes. Most
  requirements are statute/regulation (`policy`); a handful are marked `operational` (🛠) because
  they trace to official DOL agency operating guidance (identity proofing, information requested at
  filing, job-search registration) — the intended use of the operational flag, **never** legacy-system
  screening logic. Use it as the reference for house style, structure, actor lanes, and the
  policy-vs-operational distinction.
- `examples/nj-ui-weekly-certification.json` — a complete worked example (New Jersey UI weekly
  claimant certification): 66 requirements across 11 steps, three authority tiers (federal
  regulation → state statute → state regulation), three actor lanes, and a crosscut for federal
  safeguards (confidentiality, BAM quality control, pay-when-due). Use it as the reference for:
  **unique `"<Area> — <Unique name>"` topics** on every requirement; `authority` conflict callouts
  where an outdated regulation diverges from an amended statute (INT-06) and where a federal floor
  bounds a state rule (WS-06, AA-03); `gap` entries that flag legacy-system thresholds deliberately
  excluded because no policy document supports them (EARN-01's undefined "full-time work" vs. the
  legacy 32-hour proxy) — the model for keeping non-policy artifacts out while still surfacing the
  hole they papered over; and mixed `citationUrl` sourcing (eCFR + Cornell LII + FindLaw, with
  `null`-URL internal sources listed as plain text in `meta.sources`).
