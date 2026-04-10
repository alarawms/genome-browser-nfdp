#!/usr/bin/env python3
"""Convert Animal QTLdb GFF files to BED format and JSON for the backend."""
import json
import re
import sys
from pathlib import Path


def parse_qtldb_gff(gff_path: Path, species_id: str) -> list[dict]:
    """Parse Animal QTLdb GFF file into structured records."""
    records = []
    with open(gff_path) as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            if len(parts) < 9:
                continue

            chrom = parts[0]
            start = int(parts[3]) - 1  # GFF is 1-based, BED is 0-based
            end = int(parts[4])
            score_str = parts[5]
            attrs_str = parts[8]

            # Parse attributes
            attrs = {}
            for attr in attrs_str.split(";"):
                attr = attr.strip()
                if "=" in attr:
                    key, val = attr.split("=", 1)
                    attrs[key] = val

            # Extract trait info
            trait_name = attrs.get("Name", attrs.get("QTL_type", "Unknown"))
            trait_name = trait_name.replace("_", " ").replace("%20", " ")

            # Categorize trait
            trait_category = categorize_trait(trait_name)

            score = None
            if score_str != ".":
                try:
                    score = float(score_str)
                except ValueError:
                    pass

            pubmed_id = attrs.get("PUBMED_ID", attrs.get("Pubmed_id", None))

            # Normalize chromosome name — strip "chr" prefix if present
            chrom = re.sub(r"^chr", "", chrom, flags=re.IGNORECASE)

            start = max(0, start)
            # Skip records where start >= end (invalid coordinates in QTLdb)
            if start >= end:
                continue

            qtl_id = f"{species_id}_qtl_{len(records):06d}"
            records.append(
                {
                    "id": qtl_id,
                    "species_id": species_id,
                    "chromosome": chrom,
                    "start": start,
                    "end": end,
                    "trait": trait_name,
                    "trait_category": trait_category,
                    "score": score,
                    "pubmed_id": pubmed_id,
                    "source": "Animal QTLdb",
                }
            )
    return records


def categorize_trait(trait_name: str) -> str:
    """Assign a trait category based on the trait name."""
    name = trait_name.lower()
    if any(kw in name for kw in ["milk", "lactation", "dairy", "casein"]):
        return "Milk"
    if any(kw in name for kw in ["meat", "carcass", "muscle", "tenderness"]):
        return "Meat"
    if any(kw in name for kw in ["wool", "fiber", "fleece", "cashmere"]):
        return "Wool/Fiber"
    if any(kw in name for kw in ["disease", "resistance", "immune", "parasite", "health"]):
        return "Disease Resistance"
    if any(kw in name for kw in ["fertility", "reproduction", "litter", "ovulation", "twinning"]):
        return "Reproduction"
    if any(kw in name for kw in ["weight", "growth", "body", "height", "size"]):
        return "Growth"
    return "Other"


def write_bed(records: list[dict], bed_path: Path):
    """Write records as BED format (chrom, start, end, name, score)."""
    with open(bed_path, "w") as f:
        for r in sorted(records, key=lambda x: (x["chromosome"], x["start"])):
            score = int(r["score"]) if r["score"] is not None else 0
            name = r["trait"].replace(" ", "_")[:50]
            f.write(f"{r['chromosome']}\t{r['start']}\t{r['end']}\t{name}\t{score}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: convert_qtl_to_bed.py <data_dir>")
        sys.exit(1)

    data_dir = Path(sys.argv[1])

    for species_id in ["sheep", "goat"]:
        gff_path = data_dir / "qtl" / species_id / f"{species_id}_qtldb.gff"
        if not gff_path.exists():
            print(f"  ⚠ {gff_path} not found, skipping {species_id}")
            continue

        print(f"  Converting {species_id} QTLs...")
        records = parse_qtldb_gff(gff_path, species_id)
        print(f"    Parsed {len(records)} QTLs")

        # Write JSON for backend
        json_path = data_dir / "qtl" / species_id / "qtls.json"
        with open(json_path, "w") as f:
            json.dump(records, f, indent=2)
        print(f"    ✓ {json_path}")

        # Write BED for JBrowse 2
        bed_path = data_dir / "qtl" / species_id / f"{species_id}_qtls.bed"
        write_bed(records, bed_path)
        print(f"    ✓ {bed_path}")


if __name__ == "__main__":
    main()
