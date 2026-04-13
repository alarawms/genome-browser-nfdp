#!/usr/bin/env bash
# Chain the per-animal pipeline for a custom genome that has:
#   - A FASTA already registered via `make add-genome`
#   - A "donor" species whose QTLs we want to lift (e.g. sheep → najdi)
#   - A liftoff-produced GFF (on target coordinates) — optional but recommended
#   - A PAF alignment (query=donor, target=this animal) for QTL lift-over
#
# Steps performed:
#   1. Optional: bgzip + tabix the liftoff GFF if not already done
#   2. Lift donor QTLs (coords already in donor ref naming) -> target coords
#   3. Sort + bgzip + tabix the target QTL BED
#   4. Compute QTL → gene overlap against the primary GFF
#   5. Run OLS ontology enrichment on the resulting qtls.json
#
# Genomes.json must be updated manually afterward with the correct
# `gff_file`, `extra_gene_tracks`, and `qtl_bed_file` paths.
#
# Usage:
#   scripts/build_custom_animal_tracks.sh <target_id> <donor_id> <paf_path> <liftoff_gff_path>
#
# Example:
#   scripts/build_custom_animal_tracks.sh najdi sheep \
#       ~/hd1/NajdiMale_from_rambo3.liftover_alignment.cigar.paf \
#       ~/hd1/liftoff_pipeline/results/rambouillet_v3/Najdi_from_rambouillet_v3.lifted.gff3_polished

set -euo pipefail

if [ $# -lt 4 ]; then
    sed -n '1,/^# Usage:/!{/^# Example:/,/^$/p;}' "$0" | sed 's/^# //;s/^#$//'
    echo ""
    echo "Usage: $0 <target_id> <donor_id> <paf_path> <liftoff_gff_path>"
    exit 1
fi

TARGET="$1"
DONOR="$2"
PAF="$3"
LIFTOFF_GFF="$4"
DATA_DIR="${DATA_DIR:-data}"

echo "=== Build custom animal tracks: $TARGET (donor: $DONOR) ==="

mkdir -p "$DATA_DIR/annotations/$TARGET" "$DATA_DIR/qtl/$TARGET"

# --- Step 1: bgzip + tabix GFF (if source still plain) ---
GFF_OUT="$DATA_DIR/annotations/$TARGET/${TARGET}.sorted.gff3.gz"
if [ ! -f "$GFF_OUT" ]; then
    echo "--- Step 1/5: sort + bgzip + tabix GFF ---"
    if ! command -v bgzip >/dev/null 2>&1; then
        echo "  ✗ bgzip not found; install htslib or run via Docker (Dockerfile.data-pipeline)"
        exit 1
    fi
    awk '!/^#/' "$LIFTOFF_GFF" | sort -k1,1 -k4,4n | bgzip > "$GFF_OUT"
    tabix -p gff "$GFF_OUT"
    echo "  ✓ $GFF_OUT"
else
    echo "--- Step 1/5: GFF already indexed at $GFF_OUT ---"
fi

# --- Step 2: lift donor QTLs to target coords ---
DONOR_QTLS="$DATA_DIR/qtl/$DONOR/qtls.json"
TARGET_QTLS="$DATA_DIR/qtl/$TARGET/qtls.json"
FAI="$DATA_DIR/genome/$TARGET/${TARGET}.fa.gz.fai"

echo "--- Step 2/5: lift QTLs $DONOR -> $TARGET ---"
if [ ! -f "$DONOR_QTLS" ]; then
    echo "  ✗ no donor qtls at $DONOR_QTLS — run convert_qtl_to_bed.py on $DONOR first"
    exit 1
fi
FAI_ARG=""
[ -f "$FAI" ] && FAI_ARG="--target-fai $FAI"
python3 scripts/lift_qtls.py "$DONOR_QTLS" "$PAF" "$TARGET_QTLS" \
    --species-id "$TARGET" $FAI_ARG

# --- Step 3: bgzipped BED of target QTLs ---
echo "--- Step 3/5: write + index target QTL BED ---"
BED_DIR="$DATA_DIR/qtl/$TARGET"
python3 -c "
import json
from pathlib import Path
recs = json.load(open('$TARGET_QTLS'))
with open('$BED_DIR/${TARGET}_qtls.bed', 'w') as f:
    for r in sorted(recs, key=lambda x: (x['chromosome'], x['start'])):
        name = (r.get('trait') or 'QTL').replace(' ', '_')[:50]
        score = int(r.get('score') or 0)
        f.write(f\"{r['chromosome']}\\t{r['start']}\\t{r['end']}\\t{name}\\t{score}\\n\")
print(f'  wrote {len(recs)} BED records')
"
rm -f "$BED_DIR/${TARGET}_qtls.sorted.bed.gz" "$BED_DIR/${TARGET}_qtls.sorted.bed.gz.tbi"
sort -k1,1 -k2,2n "$BED_DIR/${TARGET}_qtls.bed" | bgzip > "$BED_DIR/${TARGET}_qtls.sorted.bed.gz"
tabix -p bed "$BED_DIR/${TARGET}_qtls.sorted.bed.gz"
echo "  ✓ $BED_DIR/${TARGET}_qtls.sorted.bed.gz"

# --- Step 4: QTL-gene overlap ---
echo "--- Step 4/5: QTL-gene overlap ---"
python3 scripts/compute_qtl_gene_overlap.py "$TARGET_QTLS" "$GFF_OUT"

# --- Step 5: ontology enrichment (idempotent; uses data/ontology_cache.json) ---
echo "--- Step 5/5: ontology enrichment (EBI OLS + optional BioPortal) ---"
python3 scripts/enrich_qtl_ontologies.py "$TARGET_QTLS"

echo ""
echo "=== Done. Next step: update $DATA_DIR/genomes.json ==="
echo "  Set 'gff_file' to '${TARGET}.sorted.gff3.gz'"
echo "  Set 'qtl_bed_file' to '${TARGET}_qtls.sorted.bed.gz'"
echo "  Optionally add more 'extra_gene_tracks' entries for other reference liftoffs."
echo "  Then restart the backend (touch src/backend/data_loader.py)"
