#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${1:-data}"

download_annotation() {
    local species="$1" accession="$2"
    local outdir="$DATA_DIR/annotations/$species"
    local outfile="$outdir/$species.gff3.gz"

    mkdir -p "$outdir"
    if [ -f "$outfile" ]; then
        echo "  ✓ $outfile already exists, skipping"
        return
    fi

    echo "  Downloading $species annotations ($accession) via NCBI datasets..."
    local tmpdir
    tmpdir=$(mktemp -d)

    datasets download genome accession "$accession" \
        --include gff3 \
        --filename "$tmpdir/annotations.zip"

    unzip -q -o "$tmpdir/annotations.zip" -d "$tmpdir"
    # Find the GFF3 file
    local gff
    gff=$(find "$tmpdir/ncbi_dataset/data" -name "*.gff" -o -name "*.gff3" | head -1)

    if [ -z "$gff" ]; then
        echo "  ✗ No GFF3 found in download"
        rm -rf "$tmpdir"
        return 1
    fi

    # Compress if not already gzipped
    if file "$gff" 2>/dev/null | grep -q "gzip" || [[ "$gff" == *.gz ]]; then
        cp "$gff" "$outfile"
    else
        gzip -c "$gff" > "$outfile"
    fi

    rm -rf "$tmpdir"
    echo "  ✓ $outfile"
}

echo "=== Downloading gene annotations ==="

# Sheep — ARS-UI_Ramb_v3.0
download_annotation "sheep" "GCF_016772045.2"

# Goat — ARS1.2
download_annotation "goat" "GCF_001704415.2"

echo "=== Annotation downloads complete ==="
