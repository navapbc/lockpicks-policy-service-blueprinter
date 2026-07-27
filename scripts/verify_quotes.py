#!/usr/bin/env python3
"""
verify_quotes.py — mechanically verify every requirement `quote` in a blueprint dataset
against locally saved source text.

Usage:
    python3 scripts/verify_quotes.py DATASET.json [--sources DIR]

--sources defaults to a `sources/` folder beside the dataset. Save the clean text of every
source fetched during Step 2 into that folder (one .md/.txt per document); then every quote
in the dataset can be checked copy-exact instead of trusted.

Matching normalizes whitespace, curly quotes/apostrophes, dashes, and soft hyphens on both
sides — nothing else. A quote that fails here is either paraphrased, edited, or from a
source whose text was never saved; fix the quote or save the source before delivering.

Exit codes: 0 = all quotes found; 1 = one or more quotes not found; 2 = usage error.
"""
import argparse, json, os, re, sys

SOURCE_EXTS = {".md", ".txt", ".html", ".htm", ".xml", ".json", ".csv"}

_NORMALIZE = {
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "“": '"', "”": '"', "„": '"', "‟": '"',
    "–": "-", "—": "-", "‒": "-", "−": "-",
    "­": "", " ": " ", " ": " ", "​": "",
}


def normalize(text):
    for k, v in _NORMALIZE.items():
        text = text.replace(k, v)
    return re.sub(r"\s+", " ", text).strip()


def iter_quotes(req):
    """Yield (label, quote_text) pairs for a requirement's quote field."""
    q = req.get("quote")
    rid = req.get("id", "<no id>")
    if isinstance(q, str):
        yield rid, q
    elif isinstance(q, list):
        for j, item in enumerate(q):
            if isinstance(item, str):
                yield f"{rid}[{j}]", item
            elif isinstance(item, dict) and item.get("quote"):
                yield f"{rid}[{j}]", item["quote"]


def load_sources(sources_dir):
    corpus = {}
    for root, _dirs, files in os.walk(sources_dir):
        for name in files:
            if os.path.splitext(name)[1].lower() in SOURCE_EXTS:
                path = os.path.join(root, name)
                try:
                    text = open(path, encoding="utf-8", errors="replace").read()
                except OSError as e:
                    print(f"⚠️  Could not read {path}: {e}")
                    continue
                corpus[os.path.relpath(path, sources_dir)] = normalize(text)
    return corpus


def main():
    ap = argparse.ArgumentParser(description="Verify dataset quotes copy-exact against saved source text.")
    ap.add_argument("dataset", help="Path to the dataset JSON")
    ap.add_argument("--sources", default=None,
                    help="Folder of saved source text (default: 'sources/' beside the dataset)")
    args = ap.parse_args()

    try:
        data = json.load(open(args.dataset, encoding="utf-8"))
    except Exception as e:
        print(f"❌ Could not parse dataset JSON: {e}")
        sys.exit(2)

    dataset_dir = os.path.dirname(os.path.abspath(args.dataset))
    sources_dir = args.sources or os.path.join(dataset_dir, "sources")
    if not os.path.isdir(sources_dir):
        print(f"❌ Sources folder not found: {sources_dir}\n"
              "   Save each fetched source's clean text there during Step 2, then re-run.")
        sys.exit(2)

    corpus = load_sources(sources_dir)
    if not corpus:
        print(f"❌ No readable source files in {sources_dir}.")
        sys.exit(2)

    checked = found = 0
    misses = []
    for req in data.get("requirements", []):
        for label, quote in iter_quotes(req):
            checked += 1
            needle = normalize(quote)
            hit = next((fname for fname, text in corpus.items() if needle in text), None)
            if hit:
                found += 1
            else:
                misses.append((label, quote))

    print(f"Checked {checked} quote(s) against {len(corpus)} source file(s): "
          f"{found} verified, {len(misses)} not found.")
    for label, quote in misses:
        preview = quote if len(quote) <= 100 else quote[:97] + "..."
        print(f"❌ {label}: not found in any saved source — \"{preview}\"")
    if misses:
        print("\nEach miss is a paraphrase, an edited quote, or a source whose text was never saved.\n"
              "Fix the quote against the real text, or save the missing source into the sources folder.\n"
              "Report anything left unverified in the delivery verify tally — never present it as verified.")
        sys.exit(1)
    print("✅ Every quote traces copy-exact to saved source text.")


if __name__ == "__main__":
    main()
