#!/usr/bin/env python3
"""Compute QTL-gene overlap separately for every gene-annotation track.

Unlike compute_qtl_gene_overlap.py (which targets ONE GFF), this version
walks all GFFs registered in data/genomes.json for a species (primary +
extras) and produces a per-track overlap map on each QTL record:

    overlapping_genes_by_track: {
        "rambouillet_v3": [{...gene dicts...}],
        "hu_t2t_v1":      [...],
        "texel_v4":       [...],
        "braker3":        [...]   # if registered
    }

The top-level `overlapping_genes` field continues to mirror the PRIMARY
track for back-compat with the existing QtlDetail UI.

Track ID extraction: for a gff_file "najdi.liftoff_rambouillet.sorted.gff3.gz"
or "najdi.braker3.sorted.gff3.gz", we strip the "<species>." prefix and
the ".sorted.gff3.gz" suffix. That's the track_id used as a dict key.

Usage:
    python3 scripts/compute_per_track_overlaps.py <species_id>
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compute_qtl_gene_overlap import MAX_GENES_PER_QTL, load_genes  # reuse

PROJECT = Path(__file__).resolve().parent.parent


def track_id_from_filename(species_id: str, filename: str) -> str:
    """Derive a short track_id from the on-disk filename."""
    stem = filename
    prefixes = [f"{species_id}.liftoff_", f"{species_id}.", f"liftoff_"]
    for p in prefixes:
        if stem.startswith(p):
            stem = stem[len(p):]
            break
    for suffix in (".sorted.gff3.gz", ".gff3.gz", ".gff.gz", ".gff3", ".gff"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    return stem or filename


def overlaps_for_qtl(qs: int, qe: int, genes: list[dict]) -> list[dict]:
    """Binary search could help; linear sweep is fine for our size."""
    out = []
    for g in genes:
        if g["end"] <= qs:
            continue
        if g["start"] >= qe:
            break
        out.append(g)
        if len(out) >= MAX_GENES_PER_QTL:
            break
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("species_id")
    p.add_argument("--data-dir", default="data")
    args = p.parse_args()

    data_dir = Path(args.data_dir)
    genomes_path = data_dir / "genomes.json"
    if not genomes_path.exists():
        sys.exit(f"✗ {genomes_path} not found")
    meta = json.loads(genomes_path.read_text())
    entry = meta.get(args.species_id)
    if not entry:
        sys.exit(f"✗ species '{args.species_id}' not in genomes.json")

    # Assemble ordered list of (track_id, label, file) with primary first
    tracks: list[tuple[str, str, str]] = []
    if entry.get("gff_file"):
        tid = track_id_from_filename(args.species_id, entry["gff_file"])
        tracks.append((tid, entry.get("gff_track_label", "Genes"), entry["gff_file"]))
    for ex in entry.get("extra_gene_tracks") or []:
        tid = track_id_from_filename(args.species_id, ex["file"])
        tracks.append((tid, ex.get("label", tid), ex["file"]))

    if not tracks:
        sys.exit(f"✗ no gene tracks registered for {args.species_id}")

    qtls_path = data_dir / "qtl" / args.species_id / "qtls.json"
    if not qtls_path.exists():
        sys.exit(f"✗ {qtls_path} not found")
    qtls = json.loads(qtls_path.read_text())
    print(f"Loaded {len(qtls)} QTLs for {args.species_id}; {len(tracks)} gene tracks")

    # Load each GFF into per-chromosome sorted gene lists
    track_genes: dict[str, dict[str, list[dict]]] = {}
    for tid, label, filename in tracks:
        gff_path = data_dir / "annotations" / args.species_id / filename
        if not gff_path.exists():
            print(f"  ⚠ {filename} missing on disk, skipping")
            continue
        genes = load_genes(gff_path)
        total = sum(len(v) for v in genes.values())
        track_genes[tid] = genes
        print(f"  • {tid:<24s} {total:>6d} genes   ({label})")

    # For each QTL, compute overlaps per track
    stats: dict[str, int] = {t: 0 for t in track_genes}
    for qtl in qtls:
        chrom = qtl["chromosome"]
        qs, qe = qtl["start"], qtl["end"]
        by_track: dict[str, list[dict]] = {}
        for tid, genes in track_genes.items():
            overlaps = overlaps_for_qtl(qs, qe, genes.get(chrom, []))
            by_track[tid] = overlaps
            if overlaps:
                stats[tid] += 1
        qtl["overlapping_genes_by_track"] = by_track
        # Legacy field mirrors the primary track
        primary_tid = tracks[0][0]
        qtl["overlapping_genes"] = by_track.get(primary_tid, [])
        qtl["overlapping_gene_count"] = len(qtl["overlapping_genes"])

    # Summary
    print(f"\n=== Per-track QTL hit rates (of {len(qtls)} QTLs) ===")
    for tid, count in stats.items():
        pct = 100 * count / len(qtls) if qtls else 0
        print(f"  {tid:<24s} {count:>4d} QTLs with ≥1 overlap ({pct:.0f}%)")

    qtls_path.write_text(json.dumps(qtls, indent=2, ensure_ascii=False))
    print(f"\n✓ Rewrote {qtls_path}")


if __name__ == "__main__":
    main()
