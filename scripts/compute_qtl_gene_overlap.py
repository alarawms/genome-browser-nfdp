#!/usr/bin/env python3
"""Augment qtls.json with `overlapping_genes` from a gene-annotation GFF.

For each QTL record, find all `gene` features in the GFF whose interval
overlaps the QTL's position. Attach them as minimal dicts so the frontend
can display gene chips (symbol, description, NCBI GeneID for linkout).

Usage:
  python3 scripts/compute_qtl_gene_overlap.py <path/to/qtls.json> <path/to/genes.sorted.gff3.gz>

The GFF should be bgzipped + tabix-indexed; we stream it with gzip. Only
`gene` feature rows are considered (mRNA/exon/CDS are ignored for overlap
reporting). Capped at 200 overlapping genes per QTL.
"""
import argparse
import gzip
import json
import re
from collections import defaultdict
from pathlib import Path
from statistics import median

MAX_GENES_PER_QTL = 200
GENEID_RE = re.compile(r"GeneID:(\d+)")


def load_genes(gff_path: Path) -> dict[str, list[dict]]:
    """Parse gene-type features into per-chromosome sorted lists."""
    by_chrom: dict[str, list[dict]] = defaultdict(list)
    opener = gzip.open if str(gff_path).endswith(".gz") else open
    with opener(gff_path, "rt") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9 or parts[2] != "gene":
                continue
            try:
                start = int(parts[3]) - 1
                end = int(parts[4])
            except ValueError:
                continue
            attrs = {}
            for a in parts[8].split(";"):
                if "=" in a:
                    k, v = a.split("=", 1)
                    attrs[k] = v
            name = attrs.get("Name") or attrs.get("gene") or attrs.get("ID", "")
            symbol = name if name and not name.startswith("LOC") else None
            description = (attrs.get("description") or "").replace("%20", " ").replace("%2C", ",") or None
            m = GENEID_RE.search(attrs.get("Dbxref") or "")
            by_chrom[parts[0]].append({
                "id": attrs.get("ID", "").removeprefix("gene-"),
                "name": name,
                "symbol": symbol,
                "description": description,
                "ncbi_gene_id": m.group(1) if m else None,
                "biotype": attrs.get("gene_biotype"),
                "start": start,
                "end": end,
            })
    for chrom in by_chrom:
        by_chrom[chrom].sort(key=lambda g: g["start"])
    return dict(by_chrom)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("qtls_json", type=Path)
    p.add_argument("gff", type=Path)
    args = p.parse_args()

    genes_by_chrom = load_genes(args.gff)
    total_genes = sum(len(v) for v in genes_by_chrom.values())
    print(f"Loaded {total_genes} gene records across {len(genes_by_chrom)} chromosomes from {args.gff.name}")

    qtls = json.loads(args.qtls_json.read_text())
    counts = []
    named_counts = []
    for qtl in qtls:
        chrom = qtl["chromosome"]
        qs, qe = qtl["start"], qtl["end"]
        overlaps = []
        for g in genes_by_chrom.get(chrom, []):
            if g["end"] <= qs:
                continue
            if g["start"] >= qe:
                break
            overlaps.append(g)
            if len(overlaps) >= MAX_GENES_PER_QTL:
                break
        qtl["overlapping_genes"] = overlaps
        qtl["overlapping_gene_count"] = len(overlaps)
        counts.append(len(overlaps))
        named_counts.append(sum(1 for g in overlaps if g["symbol"]))

    print(f"\n=== Overlap stats ===")
    print(f"  QTLs with >=1 overlap:      {sum(1 for c in counts if c)}/{len(qtls)}")
    print(f"  QTLs with >=1 named symbol: {sum(1 for c in named_counts if c)}/{len(qtls)}")
    print(f"  Total gene instances:       {sum(counts)}")
    print(f"  Median overlap count:       {median(counts) if counts else 0:.0f}")
    print(f"  Max overlap count:          {max(counts) if counts else 0}")

    args.qtls_json.write_text(json.dumps(qtls, indent=2, ensure_ascii=False))
    print(f"\n✓ Rewrote {args.qtls_json}")


if __name__ == "__main__":
    main()
