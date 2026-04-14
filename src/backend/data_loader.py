import gzip
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

from src.backend.jbrowse_config import get_species_meta

_GENEID_RE = re.compile(r"GeneID:(\d+)")


def _records_without_nan(df: pd.DataFrame) -> list[dict]:
    """Convert DataFrame to list[dict], coercing NaN -> None for JSON compatibility."""
    out = df.to_dict(orient="records")
    for rec in out:
        for k, v in rec.items():
            if isinstance(v, float) and math.isnan(v):
                rec[k] = None
    return out


class DataStore:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self._qtl_frames: dict[str, pd.DataFrame] = {}
        # species_id -> chromosome -> list[gene dict {start, end, symbol, name,
        #   description, ncbi_gene_id}], sorted by start
        self._genes: dict[str, dict[str, list[dict]]] = {}
        # species_id -> track_id -> chromosome -> [gene dicts]; loaded lazily
        # to keep startup memory bounded if a species has many tracks.
        self._track_genes: dict[str, dict[str, dict[str, list[dict]]]] = {}
        # species_id -> chromosome -> length
        self._chrom_lengths: dict[str, dict[str, int]] = {}
        # species_id -> comparison.json contents (precomputed by
        # scripts/compare_annotations.py, loaded on first access)
        self._annotation_comparisons: dict[str, dict] = {}
        self._load_all()

    def _load_all(self):
        qtl_dir = self.data_dir / "qtl"
        if qtl_dir.exists():
            for species_dir in qtl_dir.iterdir():
                if not species_dir.is_dir():
                    continue
                json_path = species_dir / "qtls.json"
                if json_path.exists():
                    with open(json_path) as f:
                        data = json.load(f)
                    if data:
                        self._qtl_frames[species_dir.name] = pd.DataFrame(data)

        # Chromosome lengths (from .fai) and gene indexes (from primary GFF).
        # Gracefully skips species whose FASTA/GFF hasn't been populated yet.
        meta = get_species_meta(str(self.data_dir))
        for species_id, info in meta.items():
            self._load_chrom_lengths(species_id, info)
            self._load_genes(species_id, info)

    def _load_chrom_lengths(self, species_id: str, info: dict):
        fasta_file = info.get("fasta_file")
        if not fasta_file:
            return
        fai = self.data_dir / "genome" / species_id / f"{fasta_file}.fai"
        if not fai.exists():
            return
        lengths = {}
        with open(fai) as f:
            for line in f:
                parts = line.split("\t")
                if len(parts) >= 2:
                    lengths[parts[0]] = int(parts[1])
        if lengths:
            self._chrom_lengths[species_id] = lengths

    def _load_genes(self, species_id: str, info: dict):
        gff_file = info.get("gff_file")
        if not gff_file:
            return
        gff = self.data_dir / "annotations" / species_id / gff_file
        if not gff.exists():
            return
        genes_by_chrom: dict[str, list[dict]] = defaultdict(list)
        opener = gzip.open if str(gff).endswith(".gz") else open
        with opener(gff, "rt") as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                parts = line.rstrip("\n").split("\t")
                if len(parts) < 9 or parts[2] != "gene":
                    continue
                try:
                    start = int(parts[3]) - 1
                    end = int(parts[4])
                except ValueError:
                    continue
                # Parse just the attributes we need for search + chromosome view
                name = None
                description = None
                dbxref = None
                for a in parts[8].split(";"):
                    if a.startswith("Name="):
                        name = a[5:]
                    elif a.startswith("description="):
                        description = a[12:].replace("%20", " ").replace("%2C", ",")
                    elif a.startswith("Dbxref="):
                        dbxref = a[7:]
                symbol = name if name and not name.startswith("LOC") else None
                m = _GENEID_RE.search(dbxref or "")
                genes_by_chrom[parts[0]].append({
                    "start": start,
                    "end": end,
                    "symbol": symbol,
                    "name": name or "",
                    "description": description,
                    "ncbi_gene_id": m.group(1) if m else None,
                })
        # Sort each chromosome's gene list once for fast binning + overlap
        for chrom in genes_by_chrom:
            genes_by_chrom[chrom].sort(key=lambda g: g["start"])
        if genes_by_chrom:
            self._genes[species_id] = dict(genes_by_chrom)

    # --- Public query helpers ---------------------------------------------

    def list_chromosomes(self, species_id: str) -> list[dict]:
        """Return [{'name': str, 'length': int, 'gene_count': int, 'qtl_count': int}]."""
        lengths = self._chrom_lengths.get(species_id, {})
        genes = self._genes.get(species_id, {})
        qtl_df = self._qtl_frames.get(species_id)
        qtl_counts: dict[str, int] = {}
        if qtl_df is not None and not qtl_df.empty:
            qtl_counts = qtl_df["chromosome"].value_counts().to_dict()
        result = []
        for chrom, length in lengths.items():
            result.append({
                "name": chrom,
                "length": length,
                "gene_count": len(genes.get(chrom, [])),
                "qtl_count": int(qtl_counts.get(chrom, 0)),
            })
        # natural sort by chromosome name
        def sort_key(c):
            s = c["name"]
            m = re.search(r"(\d+)", s)
            return (0, int(m.group(1))) if m else (1, s)
        result.sort(key=sort_key)
        return result

    def _genes_for_track(self, species_id: str, track_id: str | None) -> dict[str, list[dict]]:
        """Return gene-by-chromosome map for the requested track.
        If track_id is None or matches the primary, returns the cached self._genes.
        Otherwise lazy-loads the requested extra track's GFF on first access.
        """
        if not track_id:
            return self._genes.get(species_id, {})
        # Already loaded in the per-track cache?
        cached = self._track_genes.setdefault(species_id, {}).get(track_id)
        if cached is not None:
            return cached
        # Locate the file in genomes.json (or builtin) and load
        from src.backend.jbrowse_config import get_species_meta
        from collections import defaultdict
        meta = get_species_meta(str(self.data_dir)).get(species_id) or {}
        # Try primary first
        candidates: list[str] = []
        if meta.get("gff_file"):
            candidates.append(meta["gff_file"])
        for ex in meta.get("extra_gene_tracks") or []:
            candidates.append(ex["file"])
        # Match by track_id substring/derived key
        target_file = None
        for fname in candidates:
            tid = self._derive_track_id(species_id, fname)
            if tid == track_id:
                target_file = fname
                break
        if not target_file:
            self._track_genes[species_id][track_id] = {}
            return {}
        gff = self.data_dir / "annotations" / species_id / target_file
        # If this happens to be the primary, reuse the cached parse
        if meta.get("gff_file") == target_file and species_id in self._genes:
            self._track_genes[species_id][track_id] = self._genes[species_id]
            return self._genes[species_id]
        # Otherwise stream-parse this GFF
        genes_by_chrom: dict[str, list[dict]] = defaultdict(list)
        if gff.exists():
            opener = gzip.open if str(gff).endswith(".gz") else open
            with opener(gff, "rt") as f:
                for line in f:
                    if line.startswith("#") or not line.strip():
                        continue
                    parts = line.rstrip("\n").split("\t")
                    if len(parts) < 9 or parts[2] != "gene":
                        continue
                    try:
                        start = int(parts[3]) - 1
                        end = int(parts[4])
                    except ValueError:
                        continue
                    name = description = dbxref = None
                    for a in parts[8].split(";"):
                        if a.startswith("Name="):
                            name = a[5:]
                        elif a.startswith("description="):
                            description = a[12:].replace("%20", " ").replace("%2C", ",")
                        elif a.startswith("Dbxref="):
                            dbxref = a[7:]
                    symbol = name if name and not name.startswith("LOC") else None
                    m = _GENEID_RE.search(dbxref or "")
                    genes_by_chrom[parts[0]].append({
                        "start": start, "end": end, "symbol": symbol,
                        "name": name or "", "description": description,
                        "ncbi_gene_id": m.group(1) if m else None,
                    })
            for chrom in genes_by_chrom:
                genes_by_chrom[chrom].sort(key=lambda g: g["start"])
        self._track_genes[species_id][track_id] = dict(genes_by_chrom)
        return self._track_genes[species_id][track_id]

    @staticmethod
    def _derive_track_id(species_id: str, filename: str) -> str:
        stem = filename
        for prefix in (f"{species_id}.liftoff_", f"{species_id}.", "liftoff_"):
            if stem.startswith(prefix):
                stem = stem[len(prefix):]
                break
        for suffix in (".sorted.gff3.gz", ".gff3.gz", ".gff.gz", ".gff3", ".gff"):
            if stem.endswith(suffix):
                stem = stem[: -len(suffix)]
                break
        return stem or filename

    def chromosome_summary(
        self, species_id: str, chrom: str, bins: int = 200, track: str | None = None,
    ) -> dict | None:
        """Return binned gene density + QTL list for a single chromosome.
        Pass `track` to bin against an annotation other than the primary."""
        length = self._chrom_lengths.get(species_id, {}).get(chrom)
        if not length:
            return None
        bins = max(10, min(bins, 1000))
        bin_size = max(1, length // bins)
        # Build bins
        gene_bins = [
            {"start": i * bin_size,
             "end": min((i + 1) * bin_size, length),
             "count": 0,
             "symbols": []}
            for i in range(bins)
        ]
        for g in self._genes_for_track(species_id, track).get(chrom, []):
            mid = (g["start"] + g["end"]) // 2
            idx = min(mid // bin_size, bins - 1)
            gene_bins[idx]["count"] += 1
            if g["symbol"] and len(gene_bins[idx]["symbols"]) < 5:
                gene_bins[idx]["symbols"].append(g["symbol"])
        # QTLs on this chromosome (lightweight projection)
        qtls = []
        df = self._qtl_frames.get(species_id)
        if df is not None and not df.empty:
            sub = df[df["chromosome"] == chrom]
            for rec in _records_without_nan(sub):
                qtls.append({
                    "id": rec["id"],
                    "start": int(rec["start"]),
                    "end": int(rec["end"]),
                    "trait": rec["trait"],
                    "trait_category": rec["trait_category"],
                    "breed": rec.get("breed"),
                    "overlapping_gene_count": rec.get("overlapping_gene_count") or 0,
                })
        return {
            "chromosome": chrom,
            "length": length,
            "bin_size": bin_size,
            "track": track or "primary",
            "gene_bins": gene_bins,
            "qtls": qtls,
        }

    def _load_annotation_comparison(self, species_id: str) -> dict | None:
        """Lazy-load data/annotations/<species>/comparison.json."""
        if species_id in self._annotation_comparisons:
            return self._annotation_comparisons[species_id]
        path = self.data_dir / "annotations" / species_id / "comparison.json"
        if not path.exists():
            self._annotation_comparisons[species_id] = None
            return None
        self._annotation_comparisons[species_id] = json.loads(path.read_text())
        return self._annotation_comparisons[species_id]

    def annotation_summary(self, species_id: str) -> dict | None:
        comp = self._load_annotation_comparison(species_id)
        if not comp:
            return None
        return {"species_id": species_id, "tracks": comp.get("tracks", [])}

    def annotation_pairs(self, species_id: str) -> dict | None:
        comp = self._load_annotation_comparison(species_id)
        if not comp:
            return None
        return {"species_id": species_id, "pairs": comp.get("pairs", {})}

    def get_qtls(
        self,
        species_id: str,
        chromosome: str | None = None,
        start: int | None = None,
        end: int | None = None,
        trait_category: str | None = None,
        min_score: float | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        df = self._qtl_frames.get(species_id)
        if df is None or df.empty:
            return []

        mask = pd.Series(True, index=df.index)
        if chromosome is not None:
            mask &= df["chromosome"] == chromosome
        if start is not None:
            mask &= df["end"] >= start
        if end is not None:
            mask &= df["start"] <= end
        if trait_category is not None:
            mask &= df["trait_category"] == trait_category
        if min_score is not None and "score" in df.columns:
            mask &= df["score"] >= min_score

        result = df[mask].iloc[offset : offset + limit]
        # pandas represents missing values as NaN (float), which breaks JSON
        # serialization (Starlette uses allow_nan=False). `DataFrame.where`
        # doesn't reliably replace NaN with None across object columns in all
        # pandas versions, so post-process each record instead.
        return _records_without_nan(result)

    def get_traits(self, species_id: str) -> list[dict]:
        df = self._qtl_frames.get(species_id)
        if df is None or df.empty:
            return []

        grouped = df.groupby("trait_category").agg(
            qtl_count=("id", "count"),
            name=("trait_category", "first"),
        )
        return [
            {"name": row["name"], "category": cat, "qtl_count": row["qtl_count"]}
            for cat, row in grouped.iterrows()
        ]

    def search(
        self, query: str, species_id: str | None = None, limit: int = 50
    ) -> list[dict]:
        """Rank-ordered search over genes and QTL traits.

        Ranking (lower = better):
          0  exact symbol match (case-insensitive)
          1  symbol prefix match
          2  symbol substring / locus_tag match / NCBI GeneID match
          3  gene description substring
          4  QTL trait substring (legacy behavior)
        Returns SearchResult-shaped dicts with a `type` of "gene" or "qtl".
        """
        q = query.strip().lower()
        if not q:
            return []
        ranked: list[tuple[int, dict]] = []

        # --- Gene search ----------------------------------------------------
        for sid, genes_by_chrom in self._genes.items():
            if species_id and sid != species_id:
                continue
            for chrom, genes in genes_by_chrom.items():
                for g in genes:
                    sym = g["symbol"] or ""
                    name = g["name"] or ""
                    desc = (g["description"] or "").lower()
                    sym_lc = sym.lower()
                    name_lc = name.lower()
                    rank = None
                    if sym_lc == q:
                        rank = 0
                    elif sym and sym_lc.startswith(q):
                        rank = 1
                    elif q in sym_lc:
                        rank = 2
                    elif q in name_lc:
                        rank = 2
                    elif g["ncbi_gene_id"] and q == g["ncbi_gene_id"]:
                        rank = 2
                    elif desc and q in desc:
                        rank = 3
                    if rank is None:
                        continue
                    label = sym or name
                    if g["description"]:
                        label = f"{label} — {g['description']}"
                    ranked.append((rank, {
                        "type": "gene",
                        "species_id": sid,
                        "label": label,
                        "chromosome": chrom,
                        "start": g["start"],
                        "end": g["end"],
                    }))

        # --- QTL trait search (existing behavior) ---------------------------
        for sid, df in self._qtl_frames.items():
            if species_id and sid != species_id:
                continue
            matches = df[df["trait"].str.lower().str.contains(q, na=False)]
            for _, row in matches.iterrows():
                ranked.append((4, {
                    "type": "qtl",
                    "species_id": sid,
                    "label": f"{row['trait']} QTL",
                    "chromosome": row["chromosome"],
                    "start": int(row["start"]),
                    "end": int(row["end"]),
                }))

        ranked.sort(key=lambda x: x[0])
        return [r[1] for r in ranked[:limit]]
