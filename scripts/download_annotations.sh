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
    curl -fL -o "$outfile" "$url"
    # Validate: must be gzip
    if ! file "$outfile" | grep -q "gzip"; then
        echo "  ✗ Download failed — not a valid gzip file. Check URL."
        rm -f "$outfile"
        return 1
    fi
    echo "  ✓ $outfile"
}

echo "=== Downloading gene annotations ==="

# Sheep — NCBI GFF (ARS-UI_Ramb_v3.0)
download_annotation "sheep" \
    "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/016/772/045/GCF_016772045.2_ARS-UI_Ramb_v3.0/GCF_016772045.2_ARS-UI_Ramb_v3.0_genomic.gff.gz" \
    "sheep.gff3.gz"

# Goat — Ensembl GFF3 (ARS1, release 115)
download_annotation "goat" \
    "https://ftp.ensembl.org/pub/current_gff3/capra_hircus/Capra_hircus.ARS1.115.gff3.gz" \
    "goat.gff3.gz"

echo "=== Annotation downloads complete ==="
