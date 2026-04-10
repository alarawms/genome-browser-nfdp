#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${1:-data}"

download_qtl() {
    local species="$1" url="$2" filename="$3"
    local outdir="$DATA_DIR/qtl/$species"
    local outfile="$outdir/$filename"

    mkdir -p "$outdir"
    if [ -f "$outfile" ]; then
        echo "  ✓ $outfile already exists, skipping"
        return
    fi

    echo "  Downloading $species QTL data..."
    local tmpfile="$outfile.tmp"
    if ! curl -fL -o "$tmpfile" "$url"; then
        echo "  ✗ Download failed. URL may have changed."
        echo "    Manual download instructions in the error message below."
        rm -f "$tmpfile"
        return 1
    fi

    # QTLdb may return gzipped files — decompress if needed
    if head -c 2 "$tmpfile" | od -An -tx1 | grep -q "1f 8b"; then
        echo "  Decompressing gzipped file..."
        mv "$tmpfile" "$tmpfile.gz"
        gunzip "$tmpfile.gz"
    fi

    # Validate: should be tab-separated, not HTML
    if head -5 "$tmpfile" | grep -qi "<!DOCTYPE\|<html"; then
        echo "  ✗ Got HTML instead of GFF data. URL may have changed."
        rm -f "$tmpfile"
        return 1
    fi

    mv "$tmpfile" "$outfile"
    echo "  ✓ $outfile"
}

echo "=== Downloading QTL data from Animal QTLdb ==="

# Sheep QTLs — GFF from Animal QTLdb (OAR_rambo2 build, release 58)
# NOTE: QTLdb uses tokenized URLs that change with new releases.
# If download fails, visit https://www.animalgenome.org/QTLdb/OA/index
# and download the GFF file manually to data/qtl/sheep/sheep_qtldb.gff
download_qtl "sheep" \
    "https://www.animalgenome.org/cgi-bin/QTLdb/OA/download?f=Y660yclWWas47TpwiMBql&c=26090410" \
    "sheep_qtldb.gff"

# Goat QTLs — GFF from Animal QTLdb (CHIR_ARS1 build, release 58)
# If download fails, visit https://www.animalgenome.org/QTLdb/CH/index
download_qtl "goat" \
    "https://www.animalgenome.org/cgi-bin/QTLdb/CH/download?f=ZyQN21BMus0RqtabmIOuJ&c=26090410" \
    "goat_qtldb.gff"

echo "=== QTL downloads complete ==="
