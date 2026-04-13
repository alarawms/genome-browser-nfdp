#!/usr/bin/env python3
"""Enrich a qtls.json file with ontology IDs from EBI OLS + (optional) BioPortal.

QTLdb ships human-readable ontology names (VTO_name, CMO_name, PTO_name) but
not term IDs. This script:
  1. Collects every unique ontology name across all records
  2. Looks each up via EBI OLS4 (free, no auth) for VT + CMO
  3. Optionally looks up PTO/LPT via BioPortal (requires BIOPORTAL_API_KEY)
  4. Caches results to data/ontology_cache.json so reruns are offline
  5. Rewrites qtls.json with <ont>_id and <ont>_iri fields filled in

OLS4 API:        https://www.ebi.ac.uk/ols4/api/search
BioPortal API:   https://data.bioontology.org/search   (free signup at
                 https://bioportal.bioontology.org/account)

Usage:
  python3 scripts/enrich_qtl_ontologies.py <path/to/qtls.json> [--cache <path>]

Environment variables:
  BIOPORTAL_API_KEY   if set, enables PTO/LPT lookups via BioPortal
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

# QTLdb attribute key -> EBI OLS4 ontology short name. Both well-covered.
OLS_ONTOLOGIES = {
    "vto": "vt",     # Vertebrate Trait Ontology
    "cmo": "cmo",    # Clinical Measurement Ontology
}
# QTLdb attribute key -> BioPortal ontology acronym. Requires an API key.
BIOPORTAL_ONTOLOGIES = {
    "pto": "LPT",    # Livestock Product Trait — not on OLS, only on BioPortal
}
# Combined for convenience (used for record enrichment loop)
ONTOLOGIES = {**OLS_ONTOLOGIES, **BIOPORTAL_ONTOLOGIES}

BIOPORTAL_API_KEY = os.environ.get("BIOPORTAL_API_KEY")


def ols_lookup(ontology: str, label: str, timeout: int = 10) -> dict | None:
    """Return {"id": "VT:0001259", "iri": "http://...", "label": "body mass"} or None."""
    url = (
        "https://www.ebi.ac.uk/ols4/api/search"
        f"?q={quote(label)}&ontology={ontology}&exact=true&type=class&rows=1"
    )
    req = Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "genome-browser-nfdp/0.1 (qtl-ontology-enrichment)",
    })
    try:
        with urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
    except Exception as e:
        print(f"  ⚠ OLS error for {ontology}:{label!r}: {e}", file=sys.stderr)
        return None
    docs = data.get("response", {}).get("docs", [])
    if not docs:
        return None
    d = docs[0]
    return {"id": d.get("obo_id"), "iri": d.get("iri"), "label": d.get("label")}


def bioportal_lookup(ontology: str, label: str, timeout: int = 10) -> dict | None:
    """Lookup a term via BioPortal. Requires BIOPORTAL_API_KEY env var.

    Returns {"id": "LPT:0010002", "iri": "http://...", "label": "..."} or None.
    BioPortal returns full IRIs; we derive the OBO-style short ID from the
    last path segment (e.g. .../LPT_0010002 -> LPT:0010002).
    """
    if not BIOPORTAL_API_KEY:
        return None
    url = (
        "https://data.bioontology.org/search"
        f"?q={quote(label)}&ontologies={ontology}&require_exact_match=true&pagesize=1"
    )
    req = Request(url, headers={
        "Authorization": f"apikey token={BIOPORTAL_API_KEY}",
        "Accept": "application/json",
        "User-Agent": "genome-browser-nfdp/0.1",
    })
    try:
        with urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
    except Exception as e:
        print(f"  ⚠ BioPortal error for {ontology}:{label!r}: {e}", file=sys.stderr)
        return None
    coll = data.get("collection", [])
    if not coll:
        return None
    d = coll[0]
    iri = d.get("@id")
    short_id = None
    if iri:
        tail = iri.rsplit("/", 1)[-1]
        # Convert e.g. LPT_0010002 -> LPT:0010002 (OBO convention)
        if "_" in tail:
            short_id = tail.replace("_", ":", 1)
        else:
            short_id = tail
    return {"id": short_id, "iri": iri, "label": d.get("prefLabel")}


def collect_unique_names(records: list[dict]) -> dict[str, set[str]]:
    """ontology_key -> {names...}  where ontology_key is vto/cmo/pto."""
    unique: dict[str, set[str]] = {k: set() for k in ONTOLOGIES}
    for r in records:
        for k in ONTOLOGIES:
            name = r.get(f"{k}_name")
            if name:
                unique[k].add(name)
    return unique


def main():
    p = argparse.ArgumentParser()
    p.add_argument("qtls_json", type=Path)
    p.add_argument("--cache", type=Path, default=Path("data/ontology_cache.json"))
    p.add_argument("--sleep", type=float, default=0.1,
                   help="delay between OLS requests (seconds)")
    args = p.parse_args()

    records = json.loads(args.qtls_json.read_text())
    print(f"Loaded {len(records)} records from {args.qtls_json}")

    # Load or init cache
    cache = {k: {} for k in ONTOLOGIES}
    if args.cache.exists():
        try:
            cache.update(json.loads(args.cache.read_text()))
            # normalise: ensure every ontology key exists
            for k in ONTOLOGIES:
                cache.setdefault(k, {})
            # If a BioPortal key is set, drop previously-cached BioPortal misses
            # so they get retried (they may have failed before because no key
            # was available, or because of an earlier mis-routed lookup).
            if BIOPORTAL_API_KEY:
                for k in BIOPORTAL_ONTOLOGIES:
                    pruned = {n: v for n, v in cache[k].items() if v is not None}
                    if len(pruned) != len(cache[k]):
                        print(f"  (BIOPORTAL_API_KEY set: dropped {len(cache[k])-len(pruned)} "
                              f"cached {k} misses for retry)")
                    cache[k] = pruned
        except Exception:
            print(f"  ⚠ cache unreadable, starting fresh", file=sys.stderr)

    unique = collect_unique_names(records)
    print("Unique names: " + "  ".join(
        f"{k.upper()}={len(unique[k])}" for k in ONTOLOGIES
    ))

    # Look up anything not cached. OLS for VT/CMO; BioPortal for LPT (if key set).
    looked_up = 0
    misses = 0
    skipped_no_key = 0

    for k, ont_name in OLS_ONTOLOGIES.items():
        for name in sorted(unique.get(k, set())):
            if name in cache[k]:
                continue
            result = ols_lookup(ont_name, name)
            cache[k][name] = result
            if result is None:
                misses += 1
            looked_up += 1
            time.sleep(args.sleep)

    for k, ont_name in BIOPORTAL_ONTOLOGIES.items():
        for name in sorted(unique.get(k, set())):
            if name in cache[k]:
                continue
            if not BIOPORTAL_API_KEY:
                skipped_no_key += 1
                continue
            result = bioportal_lookup(ont_name, name)
            cache[k][name] = result
            if result is None:
                misses += 1
            looked_up += 1
            time.sleep(args.sleep)

    print(f"Lookup queries this run: {looked_up}  (misses: {misses})")
    if skipped_no_key:
        print(f"  ⓘ Skipped {skipped_no_key} BioPortal lookups (BIOPORTAL_API_KEY not set)")
        print("    Get a free key at https://bioportal.bioontology.org/account "
              "to enable PTO/LPT enrichment.")

    # Persist cache
    args.cache.parent.mkdir(parents=True, exist_ok=True)
    args.cache.write_text(json.dumps(cache, indent=2, sort_keys=True))
    print(f"Cache written: {args.cache}")

    # Enrich records
    hits = {k: 0 for k in ONTOLOGIES}
    for r in records:
        for k in ONTOLOGIES:
            name = r.get(f"{k}_name")
            term = cache[k].get(name) if name else None
            if term:
                r[f"{k}_id"] = term["id"]
                r[f"{k}_iri"] = term["iri"]
                hits[k] += 1

    print("Enrichment coverage:")
    for k, n in hits.items():
        pct = 100 * n / len(records) if records else 0
        print(f"  {k.upper()}: {n}/{len(records)} ({pct:.0f}%)")

    args.qtls_json.write_text(json.dumps(records, indent=2))
    print(f"✓ Rewrote {args.qtls_json}")


if __name__ == "__main__":
    main()
