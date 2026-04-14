#!/usr/bin/env python3
"""Compute pairwise concordance metrics between gene-annotation tracks.

For each species and each pair of registered tracks (A, B):
  - gene_jaccard:    |A ∩ B| / |A ∪ B|   where intersection requires ≥50%
                     reciprocal interval overlap on the same chromosome
  - intersect_count: how many gene pairs matched (one A → one B)
  - unique_a_count, unique_b_count: genes in A not matched in B and vice versa
  - name_agreement:  among matched pairs, fraction where Name attributes
                     agree exactly (curated symbol identity)
  - per_track_summary: count, mean length, biotype mix, % named (non-LOC)

Output: data/annotations/<species>/comparison.json — consumed by
the /api/species/{id}/annotations/{summary,compare} endpoints.

Usage:
    python3 scripts/compare_annotations.py <species_id> [--data-dir data]
"""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compute_qtl_gene_overlap import load_genes
from compute_per_track_overlaps import track_id_from_filename

PROJECT = Path(__file__).resolve().parent.parent
RECIP_OVERLAP_THRESHOLD = 0.5  # both A and B must each cover >=50% of the other


def reciprocal_overlap_frac(a: dict, b: dict) -> float:
    overlap = max(0, min(a["end"], b["end"]) - max(a["start"], b["start"]))
    if overlap == 0:
        return 0.0
    a_len = max(1, a["end"] - a["start"])
    b_len = max(1, b["end"] - b["start"])
    return min(overlap / a_len, overlap / b_len)


def per_track_summary(track_id: str, label: str, genes_by_chrom: dict) -> dict:
    all_genes = [g for gs in genes_by_chrom.values() for g in gs]
    n = len(all_genes)
    if n == 0:
        return {"track_id": track_id, "label": label, "gene_count": 0}
    biotypes = Counter(g["biotype"] or "unknown" for g in all_genes)
    named = sum(1 for g in all_genes if g["symbol"])
    described = sum(1 for g in all_genes if g["description"])
    with_geneid = sum(1 for g in all_genes if g["ncbi_gene_id"])
    mean_len = sum(g["end"] - g["start"] for g in all_genes) / n
    return {
        "track_id": track_id,
        "label": label,
        "gene_count": n,
        "named_count": named,
        "named_pct": round(100 * named / n, 1),
        "described_count": described,
        "with_ncbi_gene_id": with_geneid,
        "mean_length_bp": int(mean_len),
        "biotype_mix": dict(biotypes.most_common(8)),
        "chromosome_count": len(genes_by_chrom),
    }


def compare_pair(genes_a: dict, genes_b: dict) -> dict:
    """Match genes by reciprocal overlap on the same chromosome."""
    matched_pairs = 0
    matched_a_ids = set()
    matched_b_ids = set()
    name_agreements = 0
    drift_distances = []

    chroms = set(genes_a.keys()) | set(genes_b.keys())
    for chrom in chroms:
        list_a = genes_a.get(chrom, [])
        list_b = genes_b.get(chrom, [])
        if not list_a or not list_b:
            continue
        # For each A, scan B (sorted) for overlaps; record best
        b_idx_start = 0
        for ai, a in enumerate(list_a):
            best_b = None
            best_frac = 0.0
            # advance pointer past genes whose end is before a's start
            while b_idx_start < len(list_b) and list_b[b_idx_start]["end"] <= a["start"]:
                b_idx_start += 1
            j = b_idx_start
            while j < len(list_b) and list_b[j]["start"] < a["end"]:
                frac = reciprocal_overlap_frac(a, list_b[j])
                if frac >= RECIP_OVERLAP_THRESHOLD and frac > best_frac:
                    best_b = (j, list_b[j])
                    best_frac = frac
                j += 1
            if best_b:
                matched_pairs += 1
                matched_a_ids.add((chrom, ai))
                matched_b_ids.add((chrom, best_b[0]))
                a_name = (a["symbol"] or a["name"] or "").lower()
                b_name = (best_b[1]["symbol"] or best_b[1]["name"] or "").lower()
                if a_name and a_name == b_name:
                    name_agreements += 1
                drift_distances.append(
                    abs(((a["start"] + a["end"]) // 2) - ((best_b[1]["start"] + best_b[1]["end"]) // 2))
                )

    total_a = sum(len(v) for v in genes_a.values())
    total_b = sum(len(v) for v in genes_b.values())
    union = total_a + total_b - matched_pairs
    drift_distances.sort()
    median_drift = drift_distances[len(drift_distances) // 2] if drift_distances else 0
    return {
        "matched_pairs": matched_pairs,
        "unique_a_count": total_a - matched_pairs,
        "unique_b_count": total_b - matched_pairs,
        "gene_jaccard": round(matched_pairs / union, 4) if union else 0.0,
        "name_agreements": name_agreements,
        "name_agreement_pct": round(100 * name_agreements / matched_pairs, 1) if matched_pairs else 0.0,
        "median_position_drift_bp": median_drift,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("species_id")
    p.add_argument("--data-dir", default="data")
    args = p.parse_args()

    data_dir = Path(args.data_dir)
    meta = json.loads((data_dir / "genomes.json").read_text())
    entry = meta.get(args.species_id)
    if not entry:
        sys.exit(f"✗ {args.species_id} not in genomes.json")

    # Ordered tracks: primary first
    track_specs: list[tuple[str, str, str]] = []
    if entry.get("gff_file"):
        tid = track_id_from_filename(args.species_id, entry["gff_file"])
        track_specs.append((tid, entry.get("gff_track_label", "Genes"), entry["gff_file"]))
    for ex in entry.get("extra_gene_tracks") or []:
        tid = track_id_from_filename(args.species_id, ex["file"])
        track_specs.append((tid, ex.get("label", tid), ex["file"]))

    print(f"=== Annotation comparison for {args.species_id} — {len(track_specs)} tracks ===")
    track_genes: dict[str, dict] = {}
    summaries = {}
    for tid, label, fname in track_specs:
        gff = data_dir / "annotations" / args.species_id / fname
        if not gff.exists():
            print(f"  ⚠ {fname} missing; skipping")
            continue
        genes = load_genes(gff)
        track_genes[tid] = genes
        summaries[tid] = per_track_summary(tid, label, genes)
        print(f"  • {tid:<24s} {summaries[tid]['gene_count']:>6d} genes  "
              f"({summaries[tid]['named_pct']}% named)  [{label}]")

    # Pairwise comparisons (a,b) where a < b
    track_ids = list(track_genes.keys())
    pairs = {}
    for i, a in enumerate(track_ids):
        for b in track_ids[i + 1:]:
            print(f"  ≡ comparing {a} vs {b}…")
            metrics = compare_pair(track_genes[a], track_genes[b])
            pairs[f"{a}__vs__{b}"] = {"a": a, "b": b, **metrics}

    out_dir = data_dir / "annotations" / args.species_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "comparison.json"
    out_path.write_text(json.dumps({
        "species_id": args.species_id,
        "tracks": list(summaries.values()),
        "pairs": pairs,
    }, indent=2))

    print(f"\n=== Pairwise concordance ===")
    for key, m in pairs.items():
        print(f"  {key:<55s}  Jaccard={m['gene_jaccard']:.3f}  "
              f"matched={m['matched_pairs']:<5d}  "
              f"name-agree={m['name_agreement_pct']:.0f}%  "
              f"drift={m['median_position_drift_bp']:,} bp")
    print(f"\n✓ Wrote {out_path}")


if __name__ == "__main__":
    main()
