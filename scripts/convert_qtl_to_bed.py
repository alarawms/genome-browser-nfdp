#!/usr/bin/env python3
"""Convert Animal QTLdb GFF files to BED format and JSON for the backend."""
import json
import re
import sys
from pathlib import Path


def load_chrom_map(species_dir: Path) -> dict:
    """Load optional chromosome remap from <species_dir>/chromosome_name_map.tsv.

    Two-column TSV: <source_name> <target_name>. When present, this replaces
    the default "strip chr prefix" behavior — used when QTLdb's Chr.N names
    need to be mapped to the reference FASTA's naming (e.g. NCBI RefSeq
    accessions like NC_056054.1 for ARS-UI_Ramb_v3.0).
    """
    map_file = species_dir / "chromosome_name_map.tsv"
    if not map_file.exists():
        return {}
    mapping = {}
    with open(map_file) as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 2:
                mapping[parts[0]] = parts[1]
    return mapping


def parse_qtldb_gff(gff_path: Path, species_id: str, chrom_map: dict | None = None) -> list[dict]:
    """Parse Animal QTLdb GFF file into structured records."""
    chrom_map = chrom_map or {}
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

            # Helper: decode QTLdb's %20/underscore encoding for display
            def clean(v):
                if v is None:
                    return None
                return v.replace("_", " ").replace("%20", " ").strip() or None

            # Extract trait info
            trait_name = attrs.get("Name", attrs.get("QTL_type", "Unknown"))
            trait_name = clean(trait_name)

            # Categorize trait (rule-based; will be augmented by ontology IDs later)
            trait_category = categorize_trait(trait_name)

            score = None
            if score_str != ".":
                try:
                    score = float(score_str)
                except ValueError:
                    pass

            # Normalize chromosome name — prefer explicit remap if provided
            # (e.g. Chr.1 -> NC_056054.1 for sheep ARS-UI_Ramb_v3.0). Otherwise
            # strip "chr" / "chr." prefix (QTLdb uses Chr.N style; earlier regex
            # ^chr left a leading dot).
            if chrom in chrom_map:
                chrom = chrom_map[chrom]
            else:
                chrom = re.sub(r"^chr[._]?", "", chrom, flags=re.IGNORECASE)

            start = max(0, start)
            # Skip records where start >= end (invalid coordinates in QTLdb)
            if start >= end:
                continue

            # Gene ID: only trust when source is NCBIgene (other sources exist)
            gene_ncbi_id = None
            if attrs.get("gene_IDsrc") == "NCBIgene" and attrs.get("gene_ID"):
                gene_ncbi_id = attrs["gene_ID"]

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
                    "trait_variant": clean(attrs.get("TraitVariant")),
                    "base_trait": clean(attrs.get("BaseTrait")),
                    "breed": clean(attrs.get("breed")),
                    "flank_marker": attrs.get("FlankMarker"),        # rsID, keep as-is
                    "p_value": attrs.get("P-value"),                 # string "2.85E-4"
                    "variance": attrs.get("Variance"),               # string "0.58%"
                    "score": score,
                    "pubmed_id": attrs.get("PUBMED_ID", attrs.get("Pubmed_id")),
                    "qtldb_id": attrs.get("QTL_ID"),
                    "qtldb_trait_id": attrs.get("trait_ID"),
                    "gene_ncbi_id": gene_ncbi_id,
                    # Ontology names (verbatim from QTLdb) — IDs filled in by
                    # scripts/enrich_qtl_ontologies.py via EBI OLS lookups.
                    "vto_name": clean(attrs.get("VTO_name")),
                    "cmo_name": clean(attrs.get("CMO_name")),
                    "pto_name": clean(attrs.get("PTO_name")),
                    "vto_id": None, "vto_iri": None,
                    "cmo_id": None, "cmo_iri": None,
                    "pto_id": None, "pto_iri": None,
                    "source": "Animal QTLdb",
                }
            )
    return records


def categorize_trait(trait_name: str) -> str:
    """Assign a trait category based on the trait name.

    Order matters — most specific categories first (e.g. Morphology's "leg"
    would be caught by a broad Growth keyword otherwise).
    """
    name = trait_name.lower()
    # Skeletal/structural measurements — distinct from Growth
    if any(kw in name for kw in [
        "jaw", "leg length", "hind leg", "foreleg", "metacarpal", "metatarsal",
        "cannon bone", "skeletal", "limb", "conformation", "bone density",
    ]):
        return "Morphology"
    # Milk & dairy products
    if any(kw in name for kw in [
        "milk", "lactation", "dairy", "casein", "cheese", "curd",
        "rennet", "coagulation", "whey",
    ]):
        return "Milk"
    # Reproduction — covers male fertility, female fertility, parturition
    if any(kw in name for kw in [
        "fertility", "reproduction", "litter", "ovulation", "twinning",
        "sperm", "semen", "fetus", "pregnancy", "offspring", "breeding",
        "conception", "parturition", "estrus", "lambing",
    ]):
        return "Reproduction"
    # Meat & muscle
    if any(kw in name for kw in [
        "meat", "carcass", "muscle", "tenderness", "marbling", "intramuscular",
    ]):
        return "Meat"
    # Wool, fiber, coat
    if any(kw in name for kw in [
        "wool", "fiber", "fibre", "fleece", "cashmere", "staple", "coat color",
    ]):
        return "Wool/Fiber"
    # Disease resistance & parasite load (FEC is standard sheep parasite phenotype)
    if any(kw in name for kw in [
        "disease", "resistance", "immune", "parasite", "health",
        "fecal egg", "nematode", "worm", "famacha",
        "ocular mucosa", "anemia", "anaemia",
    ]):
        return "Disease Resistance"
    # Growth (size-related, excluding skeletal morphology handled above)
    if any(kw in name for kw in [
        "weight", "growth", "height", "size", "gain", "birth weight",
        "average daily gain", "adg",
    ]):
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
        species_dir = data_dir / "qtl" / species_id
        gff_path = species_dir / f"{species_id}_qtldb.gff"
        if not gff_path.exists():
            print(f"  ⚠ {gff_path} not found, skipping {species_id}")
            continue

        chrom_map = load_chrom_map(species_dir)
        if chrom_map:
            print(f"  Converting {species_id} QTLs (using chromosome_name_map.tsv: "
                  f"{len(chrom_map)} mappings)...")
        else:
            print(f"  Converting {species_id} QTLs (no name map, using prefix-strip)...")
        records = parse_qtldb_gff(gff_path, species_id, chrom_map)
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
