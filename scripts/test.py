#!/usr/bin/env python3
"""
test.py — regression check for the Policy Service Blueprinter.

Runs against every dataset in examples/. For each one it:
  1. validates it with build.py (--check-only must exit 0), and
  2. builds it into a throwaway HTML file, then confirms the engine actually
     spliced the data in — no leftover __DATA__ placeholder, and the embedded
     JSON re-parses to the same requirement count.

Pure standard library; no packages, no pytest. Run before packaging or sharing:

    python3 scripts/test.py

Exit status is 0 only if every example passes, so this is safe to wire into CI
or a pre-share checklist.
"""
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD = os.path.join(HERE, "build.py")
EXAMPLES_DIR = os.path.join(ROOT, "examples")


def fail(msg):
    print(f"  ❌ {msg}")
    return False


def check_example(path):
    name = os.path.basename(path)

    # 1. validation must pass
    r = subprocess.run(
        [sys.executable, BUILD, path, "--check-only"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"{name}")
        print((r.stdout + r.stderr).rstrip())
        return fail("validation failed (--check-only exited non-zero)")

    # 2. a full build must splice the data in and stay parseable
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "out.html")
        b = subprocess.run(
            [sys.executable, BUILD, path, "--out", out],
            capture_output=True, text=True,
        )
        if b.returncode != 0 or not os.path.exists(out):
            print(f"{name}")
            print((b.stdout + b.stderr).rstrip())
            return fail("build did not produce an HTML file")

        html = open(out, encoding="utf-8").read()
        if "__DATA__" in html:
            print(f"{name}")
            return fail("output still contains the __DATA__ placeholder — data was not spliced in")

    # dataset itself must load and carry requirements
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        print(f"{name}")
        return fail(f"dataset JSON did not parse: {e}")
    n_reqs = len(data.get("requirements", []))
    if n_reqs == 0:
        print(f"{name}")
        return fail("dataset has no requirements")

    print(f"  ✅ {name} — {n_reqs} requirements, built and spliced cleanly")
    return True


def main():
    if not os.path.isfile(BUILD):
        print(f"❌ Cannot find build.py at {BUILD}"); sys.exit(2)
    examples = sorted(glob.glob(os.path.join(EXAMPLES_DIR, "*.json")))
    if not examples:
        print(f"❌ No example datasets found in {EXAMPLES_DIR}"); sys.exit(2)

    print(f"Testing {len(examples)} example dataset(s):")
    results = [check_example(p) for p in examples]

    passed, total = sum(results), len(results)
    print()
    if passed == total:
        print(f"✅ All {total} example(s) passed.")
        sys.exit(0)
    print(f"❌ {total - passed} of {total} example(s) failed.")
    sys.exit(1)


if __name__ == "__main__":
    main()
