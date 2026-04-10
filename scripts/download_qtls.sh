#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${1:-data}"

check_qtl() {
    local species="$1" filename="$2"
    local outdir="$DATA_DIR/qtl/$species"
    local outfile="$outdir/$filename"

    mkdir -p "$outdir"
    if [ -f "$outfile" ]; then
        # Validate it's not HTML
        if head -5 "$outfile" | grep -qi "<!DOCTYPE\|<html"; then
            echo "  ✗ $outfile is HTML (bad previous download), removing"
            rm -f "$outfile"
        else
            echo "  ✓ $outfile exists"
            return 0
        fi
    fi

    echo "  ⚠ $outfile not found"
    return 1
}

echo "=== Checking QTL data from Animal QTLdb ==="
echo ""
echo "  Animal QTLdb requires terms acceptance in a browser."
echo "  Automated download is not supported."
echo ""

MISSING=0

if ! check_qtl "sheep" "sheep_qtldb.gff"; then
    MISSING=1
    echo ""
    echo "  To download sheep QTLs (OAR_rambo3 build):"
    echo "    1. Open: https://www.animalgenome.org/cgi-bin/QTLdb/OA/index"
    echo "    2. Scroll to 'Downloads' → 'Maps view' → OAR_rambo3 → GFF"
    echo "    3. Accept terms, save the file"
    echo "    4. If gzipped, decompress: gunzip <filename>.gff.gz"
    echo "    5. Move to: $DATA_DIR/qtl/sheep/sheep_qtldb.gff"
    echo ""
fi

if ! check_qtl "goat" "goat_qtldb.gff"; then
    MISSING=1
    echo ""
    echo "  To download goat QTLs (CHIR_ARS1 build):"
    echo "    1. Open: https://www.animalgenome.org/cgi-bin/QTLdb/CH/index"
    echo "    2. Scroll to 'Downloads' → 'Maps view' → CHIR_ARS1 → GFF"
    echo "    3. Accept terms, save the file"
    echo "    4. If gzipped, decompress: gunzip <filename>.gff.gz"
    echo "    5. Move to: $DATA_DIR/qtl/goat/goat_qtldb.gff"
    echo ""
fi

if [ "$MISSING" -eq 1 ]; then
    echo "  ⚠ QTL data missing — browser will work without it (no QTL track)."
    echo "  Download manually when ready, then re-run: make convert-qtls prepare-tracks"
else
    echo "  ✓ All QTL data present"
fi

echo "=== QTL check complete ==="
