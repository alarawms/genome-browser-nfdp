# Saudi Arabia Livestock Genome Browser

Web-based genome browser for Saudi livestock with JBrowse 2 visualization,
trait-ontology-enriched QTLs, multi-reference gene annotation tracks, and a
chromosome-level overview panel.

## Features

- **JBrowse 2** embedded linear genome view with reference FASTA + gene + QTL tracks
- **Multi-reference gene annotations** — stack N independent gene tracks per
  species (e.g. Rambouillet + Hu T2T + Texel liftoffs) for direct visual
  comparison, plus one-command registration of new annotations via
  `make register-annotation`
- **AnnotationComparison panel** — per-track summary cards (gene count,
  % named, biotype mix) and a pairwise **concordance heatmap** with gene
  Jaccard, name agreement %, and median position drift
- **Per-track QTL ↔ gene overlap** — each QTL knows which genes *each*
  annotation source called for that position (Rambouillet says X, Hu says Y)
- **Per-track chromosome density** — the ideogram's gene density histogram
  can be flipped to any registered annotation via a chip selector
- **Chromosome overview panel** — horizontal ideogram showing QTL tick marks
  and binned gene density; click to navigate JBrowse
- **Gene + trait search** — type a gene symbol (`MSTN`), locus tag
  (`R6Z07_021498`), description (`myostatin`), or NCBI GeneID; rank-ordered
  results across genes **and** QTL traits, scoped by species or global
- **Trait ontology enrichment** — every QTL carries VT (Vertebrate Trait) and
  CMO (Clinical Measurement) IDs with linkouts to EBI OLS term pages
- **QTL explorer sidebar** — filter by trait category + chromosome, rich gene
  chips with hover tooltips, breed/rsID/PubMed linkouts
- **Custom genome pipeline** — `make add-genome` + `make build-custom-animal`
  chain to go from a FASTA + reference liftoff to a fully-interactive browser
- **Off-repo annotation pipeline** *(optional)* — `annotation_pipeline/`
  directory with a Snakemake workflow that runs AUGUSTUS + GeMoMa
  (+ optional Helixer) on a repeat-masked assembly to produce comparison tracks
  reference-independently

## Species

| Species       | Assembly             | Annotation source(s)                | QTLs |
|---------------|----------------------|-------------------------------------|------|
| Sheep         | ARS-UI_Ramb_v3.0     | NCBI Rambouillet                    | Animal QTLdb |
| Goat          | ARS1.2               | NCBI ARS1.2                         | Animal QTLdb |
| Najdi Sheep   | NLFDP1268 v1.0 (T2T) | Liftoff from Rambouillet (primary), Hu T2T, Texel | QTLdb lifted from Rambouillet |

Najdi is a Saudi sheep breed with a T2T (telomere-to-telomere) assembly.

## Architecture

```
React + TS + Tailwind          FastAPI + pandas
┌────────────────────────┐     ┌─────────────────────────────────────────┐
│ AnnotationComparison   │     │ /api/species                            │
│ ChromosomeOverview     │     │ /api/species/{id}/qtls                  │
│ SpeciesSelector        │     │ /api/species/{id}/traits                │
│ SearchBar              │ ──► │ /api/species/{id}/chromosomes           │
│ QtlExplorer            │     │ /api/species/{id}/chromosome/{chrom}/   │
│ QtlDetail (gene chips) │     │   summary[?track=…]                     │
│ GenomeBrowser          │     │ /api/species/{id}/annotations/summary   │
│   └─ JBrowse 2         │     │ /api/species/{id}/annotations/compare   │
└────────────────────────┘     │ /api/species/{id}/jbrowse-config        │
         :3003                 │ /api/search   (genes + QTL traits)      │
                               │ /data/*       (static FASTA/GFF/BED)    │
                               └─────────────────────────────────────────┘
                                                :8880
```

## Quick start — clone, run, test

```bash
git clone https://github.com/alarawms/genome-browser-nfdp
cd genome-browser-nfdp

# 1. Set up Python env (conda recommended for samtools/bgzip/tabix)
make setup
conda activate genome-browser

# 2. Frontend deps (auto-installed by make dev-frontend too)
cd src/frontend && npm install && cd ../..

# 3. Download & index sheep+goat data (~6 GB, ~10 min)
make data              # local (needs samtools/bgzip/tabix from step 1)
# or: make data-docker  # no local tools required

# 4. Run in two terminals
make dev-backend       # FastAPI on :8880 with --reload
make dev-frontend      # Vite on :3003 with HMR

# Open http://localhost:3003
```

**Prefer tmux?** One session, two windows:

```bash
tmux new-session -d -s genome 'make dev-backend'
tmux new-window -t genome 'cd src/frontend && make -C ../.. dev-frontend'
tmux attach -t genome
```

### Run the tests

```bash
make test   # 40 backend tests, <1 s
```

### Search

The header search bar matches across genes AND QTL traits:

- **Gene symbol** — `MSTN`, `LEP`, `BMP15`, `MC1R` (exact matches rank first)
- **Locus tag** — `R6Z07_021498` (Hu-style anonymous IDs)
- **Gene description** — `myostatin`, `leptin receptor` (finds genes whose
  functional description matches even when the name is a `LOC*` placeholder)
- **NCBI GeneID** — `443449` (exact numeric match)
- **QTL trait name** — `milk`, `sperm motility`, `fecal egg count`

Results are ranked (exact symbol > prefix > substring > description > QTL
trait), colored by type (emerald GENE / amber QTL), and clickable to navigate
JBrowse. Scope with the species dropdown or search globally across all species.

## Production deployment

```bash
cp .env.example .env     # edit as needed
docker compose up --build
# → http://localhost:3003 (frontend), http://localhost:8880 (API)
```

Ports match dev by default (3003, 8880) — override via `FRONTEND_PORT` /
`BACKEND_PORT` in `.env`.

**Data volume**: the compose file mounts `./data` read-only into the backend.
You must have run `make data` (or uploaded pre-built artifacts) before
`docker compose up`, since the multi-GB FASTA/GFF/BED files are gitignored.

## Adding a new animal

### Simple: reference-only genome

```bash
make add-genome \
    FASTA=/path/to/camel.fa \
    ID=camel \
    NAME="Camel" \
    ASSEMBLY=CamDro3 \
    SCIENTIFIC="Camelus dromedarius"
```

This indexes the FASTA, bgzips it for JBrowse 2, and registers the species
in `data/genomes.json`. JBrowse will render just the reference track.

### Full: liftoff gene annotation + lifted QTLs + enrichment

Prerequisites:
- A FASTA registered via `make add-genome` above
- A [liftoff](https://github.com/agshumate/Liftoff)-produced GFF in the target
  animal's coordinates (project genes from a well-annotated donor genome)
- A [minimap2](https://github.com/lh3/minimap2) PAF alignment
  (`query=donor, target=this animal`) for QTL lift-over

```bash
make build-custom-animal \
    ID=camel \
    DONOR=sheep \
    PAF=/path/alignment.paf \
    GFF=/path/camel_liftoff.gff3
```

This chains: `scripts/lift_qtls.py` → sort/bgzip/tabix → 
`compute_qtl_gene_overlap.py` → `enrich_qtl_ontologies.py`.
Requires `paftools.js` and `bgzip`/`tabix` on `PATH` (install via the
`genome-browser` conda env or run through Docker).

Finally, edit `data/genomes.json` to register the new tracks:

```json
{
  "camel": {
    "assembly_name": "CamDro3",
    "fasta_file": "camel.fa.gz",
    "gff_file": "camel.sorted.gff3.gz",
    "gff_track_label": "Genes (Rambouillet-lifted)",
    "extra_gene_tracks": [
      {"file": "camel.liftoff_alt.sorted.gff3.gz", "label": "Genes (alt ref)"}
    ],
    "qtl_bed_file": "camel_qtls.sorted.bed.gz",
    "name": "Camel",
    "scientific_name": "Camelus dromedarius",
    "chromosome_count": 37
  }
}
```

Then restart the backend — it'll pick up the new tracks from `genomes.json`
automatically.

### Chromosome name mapping (QTLdb → reference FASTA)

If you lift QTLs from QTLdb (which uses `Chr.1`, `Chr.2`, …) onto a reference
that uses a different naming convention (e.g. NCBI RefSeq `NC_*`), drop a
two-column TSV at `data/qtl/<species>/chromosome_name_map.tsv`. The QTL
converter will apply it automatically. See
`data/qtl/sheep/chromosome_name_map.tsv` for a worked example.

### Comparing multiple annotations on the same genome

The browser supports stacking up to N gene-annotation tracks per species —
useful for comparing what different tools (or different reference liftoffs)
say about the same genome.

#### Add a new annotation as a comparison track

```bash
# Drop in a new GFF3 from any source (de novo, alternative liftoff, etc.)
make register-annotation \
    ID=najdi \
    SLUG=braker3 \
    LABEL="Genes (BRAKER3 de novo)" \
    GFF=/path/to/braker3.gff3
# Add PRIMARY=1 to make it the new primary (powers QtlExplorer chips + search)
```

This sorts/bgzips/tabixes the GFF, atomically updates `data/genomes.json`,
and the new track shows up in the JBrowse track selector after a backend
reload + browser refresh.

#### Compute comparison metrics

```bash
# Per-track QTL-gene overlap (sidebar shows which annotation called which gene)
python3 scripts/compute_per_track_overlaps.py najdi

# Pairwise concordance metrics (Jaccard, name agreement, position drift)
python3 scripts/compare_annotations.py najdi
# → writes data/annotations/najdi/comparison.json
```

The browser then exposes:
- **AnnotationComparison panel** (top of the genome view) — per-track stats
  cards + pairwise concordance heatmap
- **Per-track chromosome overview** — small chip row above the ideogram lets
  you switch which annotation drives the gene density histogram
- **Per-track gene chips in QtlExplorer** — each QTL card shows what genes
  each annotation source called, grouped by track

#### Recommended annotation tools (no RNA-Seq, local workstation)

| Tool | Approach | Inputs needed | Workstation feasible? |
|------|----------|---------------|:---------------------:|
| **GeMoMa** | Cross-species comparative (protein homology + intron model) | Reference protein GFFs (e.g. Rambouillet, Hu, Texel) + target FASTA | ✅ — best quality without RNA-Seq |
| **AUGUSTUS** (standalone) | Pure ab initio (HMM gene predictor) | Target FASTA + species model (use `mammal` or train custom) | ✅ — fast baseline |
| **Funannotate** | Hybrid wrapper (Augustus + EVM) | Same as AUGUSTUS + optional protein evidence | ✅ — moderate |
| **MAKER** (without RNA-Seq) | Multi-evidence (proteins + ab initio + repeats) | Target FASTA + protein evidence | ⚠️ slow — days on workstation |
| **BRAKER3** | Augustus + GeneMark + ProtHint | Target FASTA + RNA-Seq + protein evidence | ❌ weak without RNA-Seq |
| **Liftoff** (✅ already in use) | Lift gene models from a closely-related curated reference | Reference FASTA + GFF + target FASTA | ✅ ~1 hour per reference |

**For Najdi specifically without RNA-Seq**, GeMoMa is the strongest non-liftoff
choice — it uses reference protein alignments + intron models to predict genes,
which captures both reference-known genes (with names/descriptions inherited) and
breed-specific calls.

**Ready-to-run local annotation pipeline**: the `annotation_pipeline/` directory
(gitignored — exists on your clone only) contains a bash-driven workflow that
runs AUGUSTUS + GeMoMa on a repeat-masked assembly and produces GFF3 outputs
ready for `make register-annotation`. See its own `README.md` for setup.

### Ontology enrichment

Our pipeline auto-extracts `VTO_name` / `CMO_name` / `PTO_name` attributes
from QTLdb GFFs. To resolve these names to machine-readable term IDs:

```bash
make enrich-ontologies           # runs on every qtls.json under data/qtl/
```

Queries EBI OLS4 for VT and CMO. For LPT (Livestock Product Trait, hosted
only on BioPortal), set `BIOPORTAL_API_KEY` in your environment — free
signup at https://bioportal.bioontology.org/account. Results are cached in
`data/ontology_cache.json` so reruns are offline.

## Project structure

```
├── src/
│   ├── backend/
│   │   ├── main.py              FastAPI app with lifespan DataStore
│   │   ├── models.py            Pydantic: Species, QTL (enriched), Trait
│   │   ├── data_loader.py       DataStore: QTLs + gene index + chrom lengths
│   │   ├── jbrowse_config.py    Multi-track JBrowse 2 config generator
│   │   └── routers/             species, qtls, search endpoints
│   └── frontend/src/
│       ├── App.tsx              Layout (header / sidebar / overview / JBrowse)
│       ├── api/client.ts        Typed API client
│       ├── hooks/               useSpecies, useQtlSearch
│       └── components/
│           ├── ChromosomeOverview.tsx   SVG ideogram above JBrowse
│           ├── GenomeBrowser.tsx        Embedded JBrowse 2
│           ├── QtlExplorer.tsx          Filterable sidebar
│           ├── QtlDetail.tsx            Rich gene + ontology chips
│           ├── SearchBar.tsx, SpeciesSelector.tsx
├── scripts/
│   ├── add_genome.sh                     Register a custom FASTA + index
│   ├── register_annotation.sh            One-command add of a gene track
│   ├── build_custom_animal_tracks.sh     End-to-end per-animal pipeline
│   ├── convert_qtl_to_bed.py             QTLdb GFF → BED + JSON (rich attrs)
│   ├── enrich_qtl_ontologies.py          EBI OLS + BioPortal term ID lookups
│   ├── lift_qtls.py                      paftools cross-assembly QTL lift
│   ├── compute_qtl_gene_overlap.py       QTL ↔ gene interval intersection
│   ├── compute_per_track_overlaps.py     Per-annotation overlap maps
│   ├── compare_annotations.py            Pairwise concordance metrics
│   ├── download_{genomes,annotations,qtls}.sh
│   ├── index_genomes.sh, prepare_tracks.sh
├── annotation_pipeline/         Off-repo local annotation workspace (gitignored;
│                                 bash pipeline for AUGUSTUS + GeMoMa on a
│                                 repeat-masked assembly). See its README.
├── tests/backend/               40 tests covering DataStore + API + config
├── data/
│   ├── genomes.json             Runtime per-species config (tracked)
│   ├── ontology_cache.json      Cached OLS lookups (tracked, small)
│   ├── genome/, annotations/, qtl/, comparative/   (gitignored, ~6 GB)
├── Makefile                     Orchestration
├── environment.yml              conda env (samtools, bgzip, tabix, datasets)
├── requirements.txt             Python deps
├── docker-compose.yml           Production stack
├── Dockerfile.backend / .frontend / .data-pipeline
└── .env.example                 Copy to .env for local/production config
```

## Troubleshooting

**"Gene track throws `invalid distance too far back`"** — JBrowse cached a
stale `.tbi` from a previous data swap. Hard-refresh (`Ctrl+Shift+R`) or
clear DevTools → Application → Storage.

**Tailscale access fails** — on Fedora with firewalld, add `tailscale0` to
the `trusted` zone:
```bash
sudo firewall-cmd --permanent --zone=trusted --add-interface=tailscale0
sudo firewall-cmd --reload
```

**Backend "Out of range float values are not JSON compliant: nan"** — this
was a real bug fixed in a recent commit. If you see it after a code change
involving `qtls.json`, make sure `DataStore._records_without_nan()` is still
coercing missing object-column values. Tests in `test_api.py` cover it.

**Liftoff / paftools.js not found** — these aren't installed by default.
The `genome-browser` conda env includes samtools and htslib; minimap2
(which bundles paftools.js + k8) needs separate installation:
```bash
curl -fsSL https://github.com/lh3/minimap2/releases/download/v2.28/minimap2-2.28_x64-linux.tar.bz2 | tar -xjf -
export PATH=$PWD/minimap2-2.28_x64-linux:$PATH
```

**AnimalQTLdb download URLs rotted** — the download URLs in
`scripts/download_qtls.sh` use tokens that expire between QTLdb releases.
Download manually from https://www.animalgenome.org/QTLdb/OA/index (sheep)
or .../CH/index (goat) and place at
`data/qtl/<species>/<species>_qtldb.gff`.

---

*Built for the Saudi Organization for Sanad (SOS), 2026.*
