#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${1:-data}"

download_annotation() {
    local species="$1" url="$2" filename="$3"
    local outdir="$DATA_DIR/annotations/$species"
    local outfile="$outdir/$filename"

    mkdir -p "$outdir"
    if [ -f "$outfile" ]; then
        echo "  ✓ $outfile already exists, skipping"
        return
    fi
    echo "  Downloading $species annotations..."
    curl -L -o "$outfile" "$url"
    echo "  ✓ $outfile"
}

echo "=== Downloading gene annotations ==="

# Sheep — Ensembl GFF3
download_annotation "sheep" \
    "https://ftp.ensembl.org/pub/current_gff3/ovis_aries_rambouillet/Ovis_aries_rambouillet.Oar_rambouillet_v1.0.113.gff3.gz" \
    "sheep.gff3.gz"

# Goat — Ensembl GFF3
download_annotation "goat" \
    "https://ftp.ensembl.org/pub/current_gff3/capra_hircus/Capra_hircus.ARS1.113.gff3.gz" \
    "goat.gff3.gz"

echo "=== Annotation downloads complete ==="
