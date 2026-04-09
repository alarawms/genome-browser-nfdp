#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${1:-data}"

index_genome() {
    local species="$1"
    local fa="$DATA_DIR/genome/$species/$species.fa"
    local bgz="$DATA_DIR/genome/$species/$species.fa.gz"

    if [ ! -f "$fa" ]; then
        echo "  ⚠ $fa not found, skipping $species"
        return
    fi

    # Create .fai index
    if [ ! -f "$fa.fai" ]; then
        echo "  Indexing $species FASTA..."
        samtools faidx "$fa"
        echo "  ✓ $fa.fai"
    else
        echo "  ✓ $fa.fai already exists"
    fi

    # Create bgzipped copy for JBrowse 2
    if [ ! -f "$bgz" ]; then
        echo "  Compressing $species FASTA with bgzip..."
        bgzip -c "$fa" > "$bgz"
        samtools faidx "$bgz"
        echo "  ✓ $bgz + index"
    else
        echo "  ✓ $bgz already exists"
    fi
}

echo "=== Indexing reference genomes ==="
index_genome "sheep"
index_genome "goat"
echo "=== Genome indexing complete ==="
