#!/usr/bin/env python3
"""Lift QTLs from one reference assembly to another via a PAF alignment.

Takes a source qtls.json (with chromosome names matching the PAF query side)
and a PAF from `minimap2`/`paftools.js` alignment between two assemblies.
Uses `paftools.js liftover` under the hood to project QTL coordinates,
then stitches the lifted output back to the original QTL metadata.

Usage:
  python3 scripts/lift_qtls.py <source_qtls.json> <paf_file> <target_qtls.json> \\
      [--species-id TARGET_ID] [--target-fai path/to/target.fa.gz.fai]

Requires `paftools.js` in PATH (bundled with minimap2 releases).

If --target-fai is provided, lifted records whose coordinates extend past
the target chromosome's length are dropped (paftools doesn't enforce bounds).
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

# paftools.js output col 4 = "<qname>_<qstart>_<qend>[_tN_tM]"
ID_RE = re.compile(
    r"^(?P<q>.+?)_(?P<qs>\d+)_(?P<qe>\d+)(?:_t(?P<t5>\d+))?(?:_t(?P<t3>\d+))?$"
)


def _lift_score(lift: dict) -> tuple:
    """Sort key: prefer non-truncated lifts, then span closest to source."""
    span_err = abs((lift["tend"] - lift["tstart"]) - lift["src_span"])
    return (1 if lift["truncated"] else 0, span_err)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source_json", type=Path)
    p.add_argument("paf", type=Path)
    p.add_argument("target_json", type=Path)
    p.add_argument("--species-id", default=None,
                   help="species_id to write into target records (defaults to source's)")
    p.add_argument("--target-fai", type=Path, default=None,
                   help="target .fai to drop out-of-bounds records")
    args = p.parse_args()

    if not shutil.which("paftools.js"):
        sys.exit(
            "✗ paftools.js not found in PATH.\n"
            "  Install minimap2 (bundles paftools.js + k8) from\n"
            "  https://github.com/lh3/minimap2/releases"
        )

    source = json.loads(args.source_json.read_text())
    print(f"Loaded {len(source)} QTLs from {args.source_json}")

    # Write temp BED where col 4 = record id, and indexed lookup for rejoin
    with tempfile.TemporaryDirectory() as td:
        src_bed = Path(td) / "source.bed"
        src_to_id = {}
        with open(src_bed, "w") as f:
            for r in source:
                f.write(f"{r['chromosome']}\t{r['start']}\t{r['end']}\t{r['id']}\t0\n")
                src_to_id[(r["chromosome"], r["start"], r["end"])] = r["id"]

        out_bed = Path(td) / "target.bed"
        print(f"Running paftools.js liftover …")
        with open(out_bed, "w") as out:
            res = subprocess.run(
                ["paftools.js", "liftover", str(args.paf), str(src_bed)],
                stdout=out, stderr=subprocess.PIPE, text=True,
            )
        if res.returncode != 0:
            sys.exit(f"✗ paftools liftover failed: {res.stderr}")

        # Parse lifted BED, group by source id
        lifts_by_id = defaultdict(list)
        bad_parse = 0
        with open(out_bed) as f:
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if len(parts) != 6:
                    continue
                tchrom, tstart, tend = parts[0], int(parts[1]), int(parts[2])
                m = ID_RE.match(parts[3])
                if not m:
                    bad_parse += 1
                    continue
                key = (m.group("q"), int(m.group("qs")), int(m.group("qe")))
                rid = src_to_id.get(key)
                if not rid:
                    continue
                lifts_by_id[rid].append({
                    "tchrom": tchrom, "tstart": tstart, "tend": tend,
                    "truncated": bool(m.group("t5") or m.group("t3")),
                    "src_span": key[2] - key[1],
                })
        print(f"  lifted {sum(len(v) for v in lifts_by_id.values())} entries for {len(lifts_by_id)} records")
        if bad_parse:
            print(f"  (skipped {bad_parse} rows with unparsable IDs)")

    # Optional bounds check
    chrom_len = {}
    if args.target_fai:
        with open(args.target_fai) as f:
            for line in f:
                parts = line.split("\t")
                if len(parts) >= 2:
                    chrom_len[parts[0]] = int(parts[1])

    # Emit target records, picking the best lift per source
    target = []
    dropped_oob = 0
    target_species_id = args.species_id or source[0].get("species_id", "unknown") if source else "unknown"
    for src in source:
        lifts = lifts_by_id.get(src["id"])
        if not lifts:
            continue
        best = min(lifts, key=_lift_score)
        if chrom_len:
            clen = chrom_len.get(best["tchrom"])
            if clen is None or best["tend"] > clen:
                dropped_oob += 1
                continue
        new = dict(src)
        new["id"] = f"{target_species_id}_qtl_{len(target):06d}"
        new["species_id"] = target_species_id
        new["chromosome"] = best["tchrom"]
        new["start"] = best["tstart"]
        new["end"] = best["tend"]
        # Coordinates changed — invalidate any stale gene overlap data
        new.pop("overlapping_genes", None)
        new.pop("overlapping_gene_count", None)
        target.append(new)

    print(f"\n✓ {len(target)} QTLs written ({dropped_oob} dropped for out-of-bounds)")
    args.target_json.parent.mkdir(parents=True, exist_ok=True)
    args.target_json.write_text(json.dumps(target, indent=2, ensure_ascii=False))
    print(f"  -> {args.target_json}")


if __name__ == "__main__":
    main()
