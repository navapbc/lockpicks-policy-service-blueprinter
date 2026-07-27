# Research Packet — the handoff contract

The Research Packet is the deliverable of the **`policy-analysis-protocol`** skill and the
**required input** to the Policy Service Blueprinter. No blueprint dataset may be built without a
completed packet: the dataset's `meta.research` block references it, and `scripts/build.py` fails
validation if that block is missing. This file is the canonical definition of the contract; the
protocol skill ships a copy, but this one governs.

Why it exists: the blueprinter used to map only whatever links the user pasted. The packet
guarantees every blueprint is grounded in a verified authority set — the federal framework is
always established (even for a state-focused blueprint), every citation is confirmed against the
official codifier, currency is checked, and everything unverifiable is flagged rather than
asserted.

## File conventions

- **Name:** `<domain>-research-packet.md` (e.g. `nj-ui-weekly-certification-research-packet.md`).
- **Location:** alongside the dataset JSON, so the pair can be audited and regenerated together.
- **Format:** one markdown file — a YAML front-matter **manifest** (machine-checkable) followed by
  the **narrative sections** below (human-readable).

## Manifest (YAML front matter)

```yaml
---
packet: policy-research-packet
version: 1
domain: "New Jersey UI — weekly claimant certification"
jurisdictions:
  federal: true          # always true — the federal layer is never skipped
  states: [NJ]           # empty list for federal-only
completed: 2026-07-27    # date the protocol run finished (YYYY-MM-DD)
currency_check: 2026-07-27  # date of the Step 8 currency & conformity check
steps_completed: [0, 1, 2, 3, 4, 5, 8]  # protocol steps run; 6–7 belong to the blueprint phase
verify_flags: 3          # count of open [verify] items in section 8
---
```

All manifest fields are required. `jurisdictions.federal` must be `true` — a packet that skipped
the federal layer is incomplete by definition.

## Narrative sections (all required; write "None found" rather than omitting)

Each section maps to a protocol step (see `legal-research-protocol.md` in the
`policy-analysis-protocol` skill) and to a specific place in the blueprint dataset.

| # | Section | Protocol step | The blueprinter consumes it as |
|---|---------|--------------|-------------------------------|
| 1 | **Scope & framing** — the determination being mapped, jurisdictions, slice, category | 0 | `meta.title`, column scope |
| 2 | **Federal framework** — controlling U.S.C. provisions, operative subsections, defined terms, plus generally-applicable overlays (fraud/false-claims, APA, improper-payments) | 1 | `federal_*` tier requirements; overlay crosscuts |
| 3 | **Regulations & state layers** — C.F.R. cites mapped to the statutory subsection each implements; per-state statute + admin-code cites with current-codification confirmation | 2 | `state_statute` / `state_reg` / `agency_ops` tier requirements |
| 4 | **Federal–state interaction** — which sovereign supplies the operative rule vs. only a constraint; preemption / conformity-condition / constitutional overlay; data-privacy & records-classification regimes where data use is touched | 3 | `authority` callouts; the tier anchoring decision (state-anchored vs. federal-anchored) |
| 5 | **Sub-regulatory guidance** — each item with issuing office, series/number, date, status (current / superseded / withdrawn), and weight | 4 | `nature: "operational"` requirements and their `gap` notes |
| 6 | **Case law & standard of review** — controlling/persuasive cases, citator status (`[verify]` if no licensed citator was available) | 5 | `gap` / `authority` context; usually not chips |
| 7 | **Currency & motion watch-list** — pending bills and rulemakings, each on the status ladder (introduced → passed one chamber → passed both → enacted → **in force**) with effective dates; enacted ≠ effective | 8 | `gap` currency notes; delivery-time caveats |
| 8 | **Verify-first list** — every `[verify]` flag collated in priority order: unconfirmed pinpoints, figures, citator statuses | 5, 8 | seed of the blueprinter's **verify tally**; `gap` entries |
| 9 | **Source inventory** — every document with title, layer/tier, URL (or `null` + file name for local files), and the date its current text was confirmed on the official source | all | `meta.sources`, `citationUrl` values |

## Completion checklist (the blueprinter validates this before building)

A packet is **complete** only if:

1. The manifest parses and all fields are present; `jurisdictions.federal` is `true`.
2. Section 2 (federal framework) is substantive — never "N/A", even for a state-focused blueprint.
3. Every source in section 9 carries a confirmation date against the official source
   (uscode.house.gov, ecfr.gov, govinfo.gov, the state's official codifier) — or a `[verify]` flag.
4. `currency_check` is dated, and section 7 exists (even if it reads "no motion found").
5. Section 8 collates every open `[verify]` flag, and `verify_flags` matches its count.

If any item fails, the gate is not satisfied — finish the research; do not build around it.

## The dataset side of the contract: `meta.research`

Every dataset JSON must carry:

```jsonc
"research": {
  "packet": "nj-ui-weekly-certification-research-packet.md",  // file name, kept beside the dataset
  "completed": "2026-07-27",       // manifest `completed`
  "currencyCheck": "2026-07-27",   // manifest `currency_check`
  "verifyFlags": 3                 // manifest `verify_flags`
}
```

`build.py` errors on a missing/malformed block and warns if the packet file is not found beside
the dataset.

**Legacy escape hatch — never for new work.** A dataset that predates this contract may set
`"packet": "legacy:pre-protocol"` (other fields may then be omitted). `build.py` accepts it with a
loud warning so old examples still build. Never write this value in a new dataset; it exists only
so history remains honest instead of retro-fabricating research provenance.
