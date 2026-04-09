# MVP Saudi Livestock Genome Browser — Design Spec

**Date:** 2026-04-09
**Status:** Approved
**Scope:** MVP — Sheep + Goat, no cross-species comparison

## Overview

A web-based genome browser for Saudi livestock species, starting with sheep (Ovis aries, Oar_rambouillet_v1.0) and goat (Capra hircus, CHIR_1.0). Each species is browsed independently — no cross-species comparative features in the MVP. The application embeds JBrowse 2 as a React component inside a custom UI with QTL search, trait filtering, and species switching.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Scope | MVP — Sheep + Goat | Prove the concept before scaling to 5 species |
| Cross-species | None in MVP | Keep species independent, add synteny later |
| Companion species | Goat | Closest relative to sheep, strong QTL data (~8K) |
| Data pipeline | Automated scripts | `make data` downloads, indexes, and prepares everything |
| QTL data | All available from Animal QTLdb | Bulk import, filter in the UI |
| Deployment | Local dev only (Docker Compose) | No remote deployment in MVP |
| Backend | Thin FastAPI (no PostgreSQL) | In-memory pandas for ~18K QTL rows |
| Architecture | Embedded JBrowse 2 in custom React app | Full UI control, integrated search-to-genome navigation |

## System Architecture

```
Browser (localhost:3000)
    │
    ▼
┌─────────────────────────────────────────┐
│            Docker Compose               │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  Frontend (React + JBrowse 2)   │    │
│  │  - App shell, species selector  │    │
│  │  - QTL explorer sidebar         │    │
│  │  - @jbrowse/react-linear-       │    │
│  │    genome-view (embedded)       │    │
│  │  Port 3000 (Vite dev)           │    │
│  └──────────────┬──────────────────┘    │
│                 │                        │
│  ┌──────────────┴──────┐  ┌──────────┐  │
│  │  Backend (FastAPI)  │  │  Data    │  │
│  │  - QTL search API   │  │  Volume  │  │
│  │  - Trait metadata   │  │  (mount) │  │
│  │  - JBrowse config   │  │  FASTA   │  │
│  │  - Static files     │──│  GFF3    │  │
│  │  Port 8000          │  │  BED     │  │
│  └─────────────────────┘  └──────────┘  │
└─────────────────────────────────────────┘
```

## Frontend

### Tech Stack
- React 18 + TypeScript
- Vite (build tool)
- @jbrowse/react-linear-genome-view
- Tailwind CSS

### Components

**App.tsx** — Root layout. Manages selected species state. Renders header, sidebar, and genome browser.

**SpeciesSelector.tsx** — Toggle between Sheep and Goat. Swaps the JBrowse assembly configuration and reloads QTL data from the backend.

**GenomeBrowser.tsx** — Wraps `@jbrowse/react-linear-genome-view`. Receives assembly config and track list from the backend's `/api/species/{id}/jbrowse-config` endpoint. Exposes a `navigateTo(chr, start, end)` method for the QTL explorer to call.

**QtlExplorer.tsx** — Left sidebar panel:
- Chromosome picker (buttons for chr 1-26 + X)
- Trait category checkboxes (milk, meat, wool, disease resistance, reproduction, growth)
- Scrollable result list showing matching QTLs
- Click a QTL → navigates genome browser to that position

**QtlDetail.tsx** — Expandable panel or popup showing full QTL details: trait name, genomic position, LOD/confidence score, PubMed ID (linked), source study.

**SearchBar.tsx** — Global search in the header. Queries `/api/search?q=...` for genes, QTLs, and traits by name. Results link to genome positions.

### Hooks

**useSpecies.ts** — Fetches species list, manages selected species state.

**useQtlSearch.ts** — Fetches QTLs with filters (chromosome, trait categories, position range). Debounced.

### API Client

**api/client.ts** — Thin fetch wrapper. Base URL from environment variable. Types matching backend Pydantic models.

## Backend

### Tech Stack
- Python 3.11 + FastAPI
- pandas (in-memory QTL data)
- pydantic (response models)
- uvicorn (ASGI server)

### Endpoints

**GET /api/species**
Returns list of available species with assembly info (name, scientific name, assembly version, chromosome count).

**GET /api/species/{species_id}/qtls**
Query QTLs for a species. Parameters: `chromosome`, `start`, `end`, `trait_category`, `min_score`, `limit`, `offset`. Returns QTL list with position, trait, score, PubMed ID, source.

**GET /api/species/{species_id}/traits**
List trait categories for a species with QTL counts per category.

**GET /api/search**
Global search across QTL traits and gene names. Parameters: `q` (query string), `species` (optional filter).

**GET /api/species/{species_id}/jbrowse-config**
Returns JBrowse 2 assembly + track configuration JSON for the selected species. The frontend uses this to initialize the genome view.

**STATIC /data/{species}/{type}/{filename}**
Static file serving for genome FASTA, GFF3, BED files. JBrowse 2 fetches these directly via HTTP range requests.

### Data Loading

At startup, FastAPI loads QTL data from processed JSON files into pandas DataFrames. ~10,000 sheep QTLs + ~8,000 goat QTLs = ~18,000 rows (~5 MB in memory). Filtering done with pandas queries. No database connection needed.

### Modules

**main.py** — FastAPI app creation, CORS middleware, static file mount, startup data loading.

**routers/species.py** — Species list and info endpoints.

**routers/qtls.py** — QTL query and trait listing endpoints.

**routers/search.py** — Global search endpoint.

**models.py** — Pydantic response models (Species, QTL, Trait, SearchResult).

**data_loader.py** — Reads processed QTL JSON/BED files into pandas DataFrames at startup.

**jbrowse_config.py** — Generates JBrowse 2 assembly and track configuration per species.

## Data Pipeline

Orchestrated by `make data`. All scripts in `scripts/`. Idempotent — skips already-downloaded files.

### Steps

1. **download_genomes.sh** — Fetch reference FASTA from NCBI
   - Sheep: GCF_002742125.1 (Oar_rambouillet_v1.0, ~2.7 GB)
   - Goat: GCF_001704415.2 (CHIR_1.0, ~2.7 GB)

2. **download_annotations.sh** — Fetch GFF3 gene annotations from Ensembl
   - Sheep: Ovis_aries.Oar_rambouillet_v1.0 from Ensembl
   - Goat: Capra_hircus.CHIR_1.0 from Ensembl

3. **download_qtls.sh** — Fetch QTL data from Animal QTLdb
   - Sheep: ~10,000 QTLs (CSV/GFF format)
   - Goat: ~8,000 QTLs (CSV/GFF format)

4. **index_genomes.sh** — Index with samtools
   - `samtools faidx` to create .fai index
   - `bgzip` compressed copies for JBrowse 2

5. **prepare_tracks.sh** — Prepare track files for JBrowse 2
   - Sort GFF3, bgzip, tabix index (.gff3.gz + .tbi)
   - Sort BED, bgzip, tabix index (.bed.gz + .tbi)

6. **convert_qtl_to_bed.py** — Parse Animal QTLdb format
   - Convert to BED format (for JBrowse 2 tracks)
   - Convert to JSON (for backend in-memory loading)
   - Extract trait categories

### Data Directory Layout

```
data/
├── genome/
│   ├── sheep/   — .fa, .fa.fai, .fa.gz, .fa.gz.fai, .fa.gz.gzi
│   └── goat/    — same
├── annotations/
│   ├── sheep/   — .gff3.gz, .gff3.gz.tbi
│   └── goat/    — same
└── qtl/
    ├── sheep/   — .bed.gz, .bed.gz.tbi, qtls.json
    └── goat/    — same
```

Total storage: ~6 GB (2 species instead of 5).

## File Structure

```
sheep-qtl/
├── Makefile
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
│
├── src/
│   ├── backend/
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── species.py
│   │   │   ├── qtls.py
│   │   │   └── search.py
│   │   ├── models.py
│   │   ├── data_loader.py
│   │   └── jbrowse_config.py
│   │
│   └── frontend/
│       ├── package.json
│       ├── vite.config.ts
│       ├── tsconfig.json
│       ├── index.html
│       └── src/
│           ├── main.tsx
│           ├── App.tsx
│           ├── components/
│           │   ├── GenomeBrowser.tsx
│           │   ├── SpeciesSelector.tsx
│           │   ├── QtlExplorer.tsx
│           │   ├── QtlDetail.tsx
│           │   └── SearchBar.tsx
│           ├── hooks/
│           │   ├── useSpecies.ts
│           │   └── useQtlSearch.ts
│           └── api/
│               └── client.ts
│
├── scripts/
│   ├── download_genomes.sh
│   ├── download_annotations.sh
│   ├── download_qtls.sh
│   ├── index_genomes.sh
│   ├── prepare_tracks.sh
│   └── convert_qtl_to_bed.py
│
├── data/                    (gitignored, generated by `make data`)
│   ├── genome/
│   ├── annotations/
│   └── qtl/
│
└── docs/                    (existing, kept as-is)
```

## What This MVP Does NOT Include

- No cross-species comparison or synteny
- No PostgreSQL database
- No cattle, horse, or camel
- No Saudi breed annotations
- No user authentication
- No remote deployment
- No CI/CD pipeline

These are deferred to subsequent implementation cycles.
