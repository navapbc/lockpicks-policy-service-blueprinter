#!/usr/bin/env python3
"""
package.py — build installable .skill packages for both skills in this repo.

    python3 scripts/package.py            # writes dist/*.skill

Produces:
    dist/policy-service-blueprinter.skill  (repo root skill; excludes demos, README, dist, .git,
                                            and the sibling policy-analysis-protocol skill)
    dist/policy-analysis-protocol.skill    (the precursor/research skill)

A .skill file is a zip of the skill directory (SKILL.md at the top level inside a single
folder). Runs scripts/test.py first and aborts if the regression check fails.
"""
import os, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIST = os.path.join(ROOT, "dist")

BLUEPRINTER = {
    "name": "policy-service-blueprinter",
    "root": ROOT,
    "include": ["SKILL.md", "assets", "scripts", "reference", "examples"],
    "exclude_files": {"package.py"},  # packaging tooling isn't part of the installed skill
}
PROTOCOL = {
    "name": "policy-analysis-protocol",
    "root": os.path.join(ROOT, "policy-analysis-protocol"),
    "include": ["SKILL.md", "reference"],
    "exclude_files": set(),
}


def add(zf, skill, abspath, relpath):
    if os.path.basename(abspath) in skill["exclude_files"] or os.path.basename(abspath) == ".DS_Store":
        return
    zf.write(abspath, os.path.join(skill["name"], relpath))


def build(skill):
    out = os.path.join(DIST, skill["name"] + ".skill")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in skill["include"]:
            p = os.path.join(skill["root"], item)
            if os.path.isfile(p):
                add(zf, skill, p, item)
            else:
                for dirpath, _, files in os.walk(p):
                    for f in sorted(files):
                        ap = os.path.join(dirpath, f)
                        add(zf, skill, ap, os.path.relpath(ap, skill["root"]))
    print(f"✅ {out} ({os.path.getsize(out):,} bytes)")


def main():
    r = subprocess.run([sys.executable, os.path.join(HERE, "test.py")])
    if r.returncode != 0:
        print("❌ test.py failed — not packaging."); sys.exit(1)
    os.makedirs(DIST, exist_ok=True)
    build(BLUEPRINTER)
    if os.path.isdir(PROTOCOL["root"]):
        build(PROTOCOL)
    else:
        print("ℹ️  policy-analysis-protocol/ not present (it lives in its own repo) — "
              "package it there with its own scripts/package.py.")


if __name__ == "__main__":
    main()
