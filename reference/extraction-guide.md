# Extraction guide — turning policy documents into a service-blueprint dataset

The analytical reading of policy is **not** done here. **Strongly prefer** the
**`policy-document-analysis`** skill to decompose the sources — it is the intended companion and the
source of truth for the analysis (sentence-anchored verbatim quotes, modal-verb parsing, conditions
with an explicit `else`, structured ambiguity flags, and the document-precedence hierarchy). If that
skill is **not installed**, do the same analysis inline, holding to the identical rigor — never
hand-wave a sloppy, ad-hoc extraction. Either way, this guide covers (a) producing that analysis and
(b) mapping its output into the dataset that `schema.md` describes, then modeling the actor swimlanes
and the blueprint columns.

## 0. Policy is the single source of truth (read this first)

Extract requirements from **policy documents only** — statutes, regulations, and official
sub-regulatory policy (agency operating manuals, guidance letters, policy memos). **Never** turn the
current application/form, UI screens, a legacy system's rules/screening logic/config, data
dictionaries, prior tools, or "how it works today" into requirements, tiers, columns, chips, or
input factors, and never structure the blueprint around them. Those artifacts are non-authoritative
context for scope only. Build the columns around the **policy determination's requirement areas**,
not the sections of a form or the screens of a system. Express each requirement as *what the law
requires and the constraint on it*; where policy delegates a detail to agency discretion, record that
as a constraint (`gap`/`authority`), not by importing the implementation that filled the gap. Every
requirement must trace to a verbatim quote from a policy document — if its only basis is a form or a
system's behavior, leave it out.

## 1. Scope the question

Pin down the exact determination the tool is about (e.g. "verification at initial SNAP/Medicaid
application," "the weekly UI certification decision"). One tightly-scoped determination is gold; a
whole-program tool is unusable. Confirm scope with the user if it's ambiguous.

> Record every source link in `meta.sources` — user-provided link(s) first (mark them in `note`),
> then any supporting statutes/regulations you fetched.

## 2. Analyze the sources (prefer `policy-document-analysis`)

Gather the scoped sources and run `policy-document-analysis` if it is installed. It returns, per
rule: `rule_id`, `category`, `modal_strength`, `source.citation` + `source.sentence_index[]`
(verbatim), `conditions[]` (if/then/else), `inputs[]`, `outputs[]`, `edge_cases[]`,
`ambiguity_flags[]`, and the document-precedence hierarchy. Do not proceed until each rule has passed
its validation. If the skill is not installed, produce the same per-rule fields inline, to the same
standard, before continuing.

## 3. Map analysis → dataset requirements

Translate each analyzed rule into one requirement object:

| `policy-document-analysis` field | dataset requirement field |
|---|---|
| `rule_id` | `id` |
| `source.citation` | `citation` (keep the single most specific cite; never invent one) |
| the source-doc URL for that citation (from `meta.sources`) | `citationUrl` (else `null`) — makes the citation clickable in the side panel |
| `source.sentence_index[].text` | `quote` (verbatim; join the anchored sentences the rule rests on) |
| plain-language summary + `conditions` | `statement` (implementation-facing; let `modal_strength` set how firm the wording is) |
| `category` (or a topical grouping) + a rule-specific name | `topic` — **unique per requirement**, formatted `"<Area> — <Unique name>"` (the chip shows only the unique name; no two requirements may share a `topic`) |
| `ambiguity_flags[].issue` (+ resolution status) | `gap` |
| precedence tier of the citation (see step 5) | `tier` |
| precedence relationship to a higher rule | `authority` |
| `inputs[]` that are forms/artifacts | `forms` (else `null`) |
| **who performs / enforces the rule** | **`actor`** (see step 4) |
| **strict policy vs agency operational practice** | **`nature`** (see step 4) |

Keep quotes verbatim. Aim for coverage of the determination, not the whole program. 8–40
requirements is typical.

## 4. Assign actors and nature (the core of this tool)

**Pick actor lanes that fit the policy.** The common set is `applicant` (or `claimant`),
`caseworker` (manual eligibility-worker judgment and handling), and `system` (automated data
matches, notice generation, auto-determination). Some domains need different or additional lanes
(e.g. `adjudicator`, `agency`, `board`). Declare them in `blueprint.actors[]` and give each
requirement an `actor` matching one of those keys.

Heuristics for assigning `actor`:
- **applicant/claimant** — the rule is an obligation on, or action by, the person (provide
  documents, attend the interview, return items within a deadline).
- **system** — the rule is automatable: definitional standards, electronic data matching,
  reasonable-compatibility tests, statewide notice generation, auto-determination on available info.
- **caseworker** — the rule requires human judgment or handling: questionable-information calls,
  fault attribution, refusal-vs-failure determinations, case-by-case exceptions, conducting the
  interview, seeking an explanation.

Set `nature`:
- **`policy`** (default) — a statutory/regulatory requirement. This should be the vast majority.
- **`operational`** — use **only** for a step that is itself stated in an **official policy
  document** (a published operating manual or sub-regulatory guidance) but reads as agency practice
  or delegated judgment rather than strict statute/regulation. Marking it operational keeps it
  visually distinct (dashed 🛠) so a reviewer never mistakes it for a hard legal requirement; note
  the murkiness in `gap`. **`operational` is never a channel for the current implementation or a
  legacy system** — screening logic, code tables, matrices, form fields, or system behavior are not
  policy and must be left out entirely, not relabeled operational (see §0). If you cannot point to a
  policy document, there is no requirement.

## 5. Tiers from the precedence hierarchy → `tiers`

Use the document-precedence hierarchy to define `tiers`, ranked by who controls on conflict (rank 1
= highest). Give each a `key`, `label`, `rank`, and `color`. Common shapes: federal program
with state administration (federal reg → state statute → state reg → federal guidance, federal
controls); single-sovereign federal (statute → reg → manual); state-only (statute → reg). Leave
`meta.authorityLabel`/`authorityBadge` at the default "Multiple policies" unless the user wants a
domain-specific term (e.g. "preemption").

## 6. `authority` links

Wherever one rule implements or is bounded by a higher-tier rule, attach an `authority` object:
`higher`/`lower` citations, which one `controls`, and a one-sentence `note`. **Whenever you add an
`authority` object, link its citations to sources:** set `higherUrl`/`lowerUrl` to the matching URL
from `meta.sources` (add a supporting-authority source entry if the cited reg isn't already listed).
If a side has no source URL, you may instead set `higherRef`/`lowerRef` to another requirement's `id`
for an internal cross-link; otherwise leave the side plain (never invent a URL or target).

## 7. Build the blueprint columns

Turn the analyzed `conditions` into columns (steps), in reading order. Each column gets:
- a stable `id` and a human `title` (the step is auto-labeled "Step 1", "Step 2"… by position);
- the plain-language `q` the claimant is asked;
- `inputs[]` — the factors that drive the branch at this step (pull from the rule `inputs[]` and
  conditions), shown in the dedicated Inputs swimlane;
- `reqs[]` — the requirement ids tested at this step (they distribute into actor lanes by each
  req's `actor`);
- `out[]` — the branch outcomes, each a plain-language label with a `kind` (read-only result pills).

**Cell density cap — no more than 6 requirements in a single cell.** A cell is one actor's chips at
one step (a column × actor-lane intersection). If the reqs you assign to a step put more than 6
chips in any one actor lane, that cell is too dense; split the step into two or more columns. **How
to split is the user's call, not yours** — pause and ask them, offering concrete options (e.g. by
sub-topic, by actor, by sub-phase, or by "first N vs. the rest"). Then create one column per chosen
slice, each with its own `id`, `title`, `q`, `inputs`, and its share of the `reqs`; keep them
adjacent (and in the same `group`, if grouped) so they still read as one part of the journey.
`build.py` warns when any single cell exceeds 6.

Use `group` to split columns into separate stacked tables for **alternative paths** rather than a strict sequence (e.g. a
SNAP path and a Medicaid path, or CUE/HLR/supplemental-claim lanes). Add a `crosscut` for rules that
apply across every step (confidentiality, duty-to-assist), or omit it. Every requirement should
surface in at least one column or the crosscut (the build warns about orphans).

## 8. Build and verify

Run `python3 scripts/build.py DATASET.json --out TOOL.html`. Fix every ❌ error and review ⚠️
warnings (unassigned actors, orphaned requirements, bad outcome refs). Then open the output and
confirm: actor lanes read correctly, operational flags land on the right rules, input factors and
outcome pills read correctly, alternative-path tables are split correctly, quotes/citations match the sources, and
the console is error-free.

## Sourcing notes

`policy-document-analysis` Step 1 (Document Intake) handles conversion and metadata, but you still
have to get it the source text:

- Some authoritative sources are JavaScript-rendered portals (e.g. VA's M21-1 on KnowVA) that a
  plain fetch returns empty. Use a rendering browser to read them, and prefer official static text
  (eCFR, Cornell LII, govinfo) for verbatim regulation/statute language.
- Because `policy-document-analysis` anchors every quote to an indexed sentence, feed it clean
  source text; don't paraphrase before handing it over.
