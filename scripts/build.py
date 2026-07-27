#!/usr/bin/env python3
"""
build.py — validate a Policy Service Blueprint dataset and assemble the self-contained
HTML tool by splicing the dataset into the bundled rendering engine.

Usage:
    python3 scripts/build.py DATASET.json [--out OUTPUT.html] [--template TEMPLATE.html]
    python3 scripts/build.py DATASET.json --check-only    # validate without writing

The template defaults to ../assets/template.html — the fixed engine with the locked
house style baked in. Do not pass a different template unless you know why.

Locked design patterns already baked into assets/template.html (see SKILL.md):
  1. "View sources" drawer renders local-only sources (url: null) as plain text, not a broken link.
  2. Crosscut bar: light-blue (#d9e8f6) background, dark text, serif subheading, inline row, no icon.
  3. Outcome pills have roomier padding so text never touches the border.
  4. Blueprint columns are wider (250px min) with the grid min-width forcing horizontal scroll.
Colors/labels (USWDS tier palette, empty subtitle/intro, colon-free crosscut label) live in the
dataset JSON — copy examples/blueprint-starter.json to begin a new use case.
"""
import argparse, json, os, re, sys

REQUIRED_REQ_FIELDS = ["id", "topic", "statement", "tier", "citation", "quote"]
VALID_KINDS = {"good", "bad", "partial", "nd", "na", "proc"}
VALID_NATURE = {"policy", "operational"}


def validate(data, dataset_dir=None):
    errors, warnings = [], []
    meta = data.get("meta", {})
    if not meta.get("title"):
        warnings.append("meta.title is empty — the tool will use a generic title.")

    # Research gate: every dataset must record its completed Research Packet
    # (see reference/research-packet.md — produced by the policy-analysis-protocol skill).
    research = meta.get("research")
    if not isinstance(research, dict):
        errors.append("meta.research is missing — every dataset must reference a completed Research Packet "
                      "(run the policy-analysis-protocol skill first; see reference/research-packet.md).")
    else:
        packet = research.get("packet")
        if packet == "legacy:pre-protocol":
            warnings.append("meta.research.packet is 'legacy:pre-protocol' — this dataset predates the research "
                            "gate and is NOT research-gated. Never use this value in new work.")
        elif not (isinstance(packet, str) and packet.strip()):
            errors.append("meta.research.packet must name the Research Packet file (e.g. '<domain>-research-packet.md').")
        else:
            if not packet.endswith(".md"):
                warnings.append(f"meta.research.packet '{packet}' does not look like a markdown packet file.")
            if dataset_dir is not None and not os.path.isfile(os.path.join(dataset_dir, packet)):
                warnings.append(f"Research Packet '{packet}' not found beside the dataset — keep the pair together "
                                "so the blueprint can be audited and regenerated.")
            for f in ("completed", "currencyCheck"):
                v = research.get(f)
                if not (isinstance(v, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", v)):
                    errors.append(f"meta.research.{f} must be a YYYY-MM-DD date (from the packet manifest).")
            vf = research.get("verifyFlags")
            if not (isinstance(vf, int) and vf >= 0):
                warnings.append("meta.research.verifyFlags should be the packet's open [verify] count (integer ≥ 0).")

    tiers = data.get("tiers", [])
    if not tiers:
        errors.append("tiers[] is empty — at least one tier is required.")
    tier_keys, ranks = set(), []
    for i, t in enumerate(tiers):
        for f in ("key", "label", "rank", "color"):
            if f not in t:
                errors.append(f"tiers[{i}] missing '{f}'.")
        if "key" in t:
            if not re.fullmatch(r"[a-z0-9_]+", str(t["key"])):
                errors.append(f"tiers[{i}].key '{t['key']}' must be lowercase letters/digits/underscores only.")
            if t["key"] in tier_keys:
                errors.append(f"duplicate tier key '{t['key']}'.")
            tier_keys.add(t["key"])
        if "color" in t and not re.fullmatch(r"#[0-9a-fA-F]{6}", str(t["color"])):
            warnings.append(f"tiers[{i}].color '{t.get('color')}' is not a #rrggbb hex value.")
        if "rank" in t:
            ranks.append(t["rank"])
    if ranks and len(set(ranks)) != len(ranks):
        warnings.append("tier ranks are not unique — ordering/dominant-tier may be ambiguous.")

    bp = data.get("blueprint", {})
    actors = bp.get("actors", [])
    actor_keys = set()
    if actors:
        for i, a in enumerate(actors):
            for f in ("key", "label"):
                if f not in a:
                    errors.append(f"blueprint.actors[{i}] missing '{f}'.")
            if "key" in a:
                if a["key"] in actor_keys:
                    errors.append(f"duplicate actor key '{a['key']}'.")
                actor_keys.add(a["key"])
    else:
        warnings.append("blueprint.actors[] not defined — all requirements collapse into one lane.")
    last_actor = actors[-1]["key"] if actors else "policy"

    reqs = data.get("requirements", [])
    req_actor = {r.get("id"): r.get("actor") for r in reqs}
    if not reqs:
        errors.append("requirements[] is empty.")
    ids = set()
    topics_seen = set()
    for i, r in enumerate(reqs):
        rid = r.get("id", f"<index {i}>")
        for f in REQUIRED_REQ_FIELDS:
            if not r.get(f):
                errors.append(f"requirement {rid} missing required field '{f}'.")
        if r.get("id") in ids:
            errors.append(f"duplicate requirement id '{r.get('id')}'.")
        ids.add(r.get("id"))
        if r.get("topic") and r["topic"] in topics_seen:
            errors.append(f"requirement {rid} duplicates topic '{r['topic']}' — every requirement needs a unique topic (it is the chip label); use \"<Area> — <Unique name>\".")
        topics_seen.add(r.get("topic"))
        q = r.get("quote")
        if isinstance(q, list):
            if not q:
                errors.append(f"requirement {rid} quote[] is empty — use a string or a non-empty array.")
            for j, item in enumerate(q):
                if isinstance(item, str):
                    if not item.strip():
                        errors.append(f"requirement {rid} quote[{j}] is an empty string.")
                elif isinstance(item, dict):
                    if not item.get("quote"):
                        errors.append(f"requirement {rid} quote[{j}] object missing 'quote' text.")
                else:
                    errors.append(f"requirement {rid} quote[{j}] must be a string or {{quote, citation}} object.")
        if r.get("tier") and r["tier"] not in tier_keys:
            errors.append(f"requirement {rid} has tier '{r['tier']}' not declared in tiers[].")
        if actors and r.get("actor") and r["actor"] not in actor_keys:
            warnings.append(f"requirement {rid} actor '{r['actor']}' is not a declared actor lane — it will fall into the last lane.")
        if actors and not r.get("actor"):
            warnings.append(f"requirement {rid} has no actor — it will fall into the last lane.")
        if r.get("nature") and r["nature"] not in VALID_NATURE:
            warnings.append(f"requirement {rid} nature '{r['nature']}' should be one of {sorted(VALID_NATURE)} (default policy).")
        a = r.get("authority")
        if a:
            for f in ("higher", "lower", "controls", "note"):
                if f not in a:
                    errors.append(f"requirement {rid} authority missing '{f}'.")
            for uf in ("higherUrl", "lowerUrl"):
                u = a.get(uf)
                if u is not None and not (isinstance(u, str) and u.startswith("http")):
                    warnings.append(f"requirement {rid} authority {uf} should be an http(s) URL or null.")
        if r.get("forms") is not None and not isinstance(r["forms"], list):
            errors.append(f"requirement {rid} forms must be a list or null.")
        cu = r.get("citationUrl")
        if cu is not None and not (isinstance(cu, str) and cu.startswith("http")):
            warnings.append(f"requirement {rid} citationUrl should be an http(s) URL or null.")

    cols = bp.get("columns", [])
    if not cols:
        errors.append("blueprint.columns[] is empty — nothing to render.")
    col_ids, placed = set(), set()
    for i, c in enumerate(cols):
        cid = c.get("id", f"<index {i}>")
        if not c.get("id"):
            errors.append(f"blueprint.columns[{i}] missing 'id'.")
        elif c["id"] in col_ids:
            errors.append(f"duplicate blueprint column id '{c['id']}'.")
        col_ids.add(c.get("id"))
        if not c.get("title") and not c.get("q"):
            warnings.append(f"blueprint column {cid} has neither title nor question — its header will be blank.")
        if c.get("inputs") is not None and not isinstance(c["inputs"], list):
            errors.append(f"blueprint column {cid} inputs must be a list or null.")
        lane_counts = {}
        for rid in c.get("reqs", []):
            act = req_actor.get(rid)
            lane = act if (act in actor_keys) else last_actor
            lane_counts[lane] = lane_counts.get(lane, 0) + 1
        if lane_counts and max(lane_counts.values()) > 6:
            worst = max(lane_counts, key=lane_counts.get)
            warnings.append(f"blueprint column {cid} has {lane_counts[worst]} requirements in the '{worst}' cell (>6) — too dense; split the step.")
        for rid in c.get("reqs", []):
            if rid not in ids:
                errors.append(f"blueprint column {cid} references unknown requirement '{rid}'.")
            placed.add(rid)
        for o in c.get("out", []):
            if o.get("kind") not in VALID_KINDS:
                warnings.append(f"blueprint column {cid} outcome kind '{o.get('kind')}' unexpected (expected {sorted(VALID_KINDS)}).")

    cc = bp.get("crosscut")
    if cc:
        for rid in cc.get("reqs", []):
            if rid not in ids:
                errors.append(f"blueprint.crosscut references unknown requirement '{rid}'.")
            placed.add(rid)

    orphans = ids - placed
    if orphans:
        warnings.append(f"{len(orphans)} requirement(s) not shown in any column or crosscut: {sorted(orphans)}")
    return errors, warnings


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="Validate a dataset and build a Policy Service Blueprint HTML tool.")
    ap.add_argument("dataset", help="Path to the dataset JSON")
    ap.add_argument("--template", default=os.path.join(here, "..", "assets", "template.html"))
    ap.add_argument("--out", default=None, help="Output HTML path (default: alongside dataset)")
    ap.add_argument("--check-only", action="store_true", help="Validate without writing output")
    args = ap.parse_args()

    try:
        data = json.load(open(args.dataset, encoding="utf-8"))
    except Exception as e:
        print(f"❌ Could not parse dataset JSON: {e}"); sys.exit(2)

    errors, warnings = validate(data, dataset_dir=os.path.dirname(os.path.abspath(args.dataset)))
    for w in warnings:
        print(f"⚠️  {w}")
    for e in errors:
        print(f"❌ {e}")
    if errors:
        print(f"\nFAILED: {len(errors)} error(s), {len(warnings)} warning(s). No output written."); sys.exit(1)

    bp = data.get("blueprint", {})
    print(f"✅ Validation passed ({len(data.get('requirements',[]))} requirements, "
          f"{len(data.get('tiers',[]))} tiers, {len(bp.get('columns',[]))} columns, "
          f"{len(bp.get('actors',[])) or 1} actor lane(s), {len(warnings)} warning(s)).")
    if args.check_only:
        return

    tpl = open(args.template, encoding="utf-8").read()
    if "__DATA__" not in tpl:
        print("❌ Template has no __DATA__ placeholder."); sys.exit(2)
    html = tpl.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    out = args.out or os.path.splitext(os.path.basename(args.dataset))[0] + ".html"
    open(out, "w", encoding="utf-8").write(html)
    print(f"✅ Wrote {out}")


if __name__ == "__main__":
    main()
