#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${1:-data}"

prepare_gff() {
    local species="$1"
    local infile="$DATA_DIR/annotations/$species/$species.gff3.gz"
    local sorted="$DATA_DIR/annotations/$species/$species.sorted.gff3.gz"

    if [ ! -f "$infile" ]; then
        echo "  ⚠ $infile not found, skipping"
        return
    fi
    if [ -f "$sorted.tbi" ]; then
        echo "  ✓ $sorted already indexed"
        return
    fi

    echo "  Sorting and indexing $species GFF3..."
    # Decompress, filter comments, sort by position, recompress, index
    zcat "$infile" | grep -v "^#" | sort -t$'\t' -k1,1 -k4,4n | bgzip > "$sorted"
    tabix -p gff "$sorted"
    echo "  ✓ $sorted + .tbi"
}

prepare_bed() {
    local species="$1"
    local infile="$DATA_DIR/qtl/$species/${species}_qtls.bed"
    local sorted="$DATA_DIR/qtl/$species/${species}_qtls.sorted.bed.gz"

    if [ ! -f "$infile" ]; then
        echo "  ⚠ $infile not found, skipping"
        return
    fi
    if [ -f "$sorted.tbi" ]; then
        echo "  ✓ $sorted already indexed"
        return
    fi

    # Skip if empty BED file (0 QTLs parsed)
    if [ ! -s "$infile" ]; then
        echo "  ⚠ $infile is empty, skipping"
        return
    fi

    echo "  Sorting and indexing $species QTL BED..."
    sort -k1,1 -k2,2n "$infile" | bgzip > "$sorted"
    tabix -p bed "$sorted"
    echo "  ✓ $sorted + .tbi"
}

echo "=== Preparing track files for JBrowse 2 ==="
for species in sheep goat; do
    prepare_gff "$species"
    prepare_bed "$species"
done
echo "=== Track preparation complete ==="
