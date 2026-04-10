# Saudi Arabia Livestock Genome Browser

Web-based genome browser for Saudi livestock species with QTL search, filtering, and embedded JBrowse 2 visualization.

**Status:** MVP complete (sheep + goat). Ready for data loading and use.

## Quick Start

```bash
# 1. Set up environment (pick one)
make setup              # Conda (recommended for local dev)
# or just have Docker installed

# 2. Download & index genome data (~6 GB)
make data               # Local (requires samtools, bgzip, tabix)
make data-docker        # Docker (no local tools needed)

# 3. Run the app
make dev-backend        # Terminal 1: FastAPI on :8000
make dev-frontend       # Terminal 2: Vite dev server on :3000
# Open http://localhost:3000
```

## Architecture

```
React + TypeScript + Tailwind     FastAPI + pandas
┌─────────────────────────┐      ┌─────────────────────┐
│  SpeciesSelector        │      │  /api/species        │
│  SearchBar              │ ───► │  /api/species/{}/qtls│
│  QtlExplorer (sidebar)  │      │  /api/search         │
│  JBrowse 2 (main view)  │      │  /api/.../jbrowse-config│
└─────────────────────────┘      │  /data/* (static)    │
        :3000                    └─────────────────────┘
                                        :8000
```

- **Frontend:** React 18, Vite, Tailwind CSS, `@jbrowse/react-linear-genome-view`
- **Backend:** FastAPI, pandas DataStore (QTLs loaded in-memory at startup)
- **Data pipeline:** Shell scripts + Python for downloading/indexing from NCBI, Ensembl, Animal QTLdb

## Species

| Species | Assembly | Annotations | QTLs |
|---------|----------|-------------|------|
| Sheep   | ARS-UI_Ramb_v3.0 (NCBI) | Ensembl GFF3 | Animal QTLdb |
| Goat    | ARS1.2 (NCBI) | Ensembl GFF3 | Animal QTLdb |

## Add a Custom Genome

For de novo assemblies or local genomes (requires `samtools` and `bgzip`):

```bash
make add-genome FASTA=/path/to/assembly.fa ID=my_species NAME="My Species" ASSEMBLY=MyAssembly_v1
```

This copies the FASTA, indexes it, and registers it in the browser. No annotations required — JBrowse 2 will display the reference sequence track.

## Project Structure

```
├── src/
│   ├── backend/
│   │   ├── main.py              # FastAPI app with lifespan
│   │   ├── models.py            # Pydantic: Species, QTL, Trait, SearchResult
│   │   ├── data_loader.py       # DataStore: pandas-backed QTL loading
│   │   ├── jbrowse_config.py    # JBrowse 2 assembly/track config generator
│   │   └── routers/             # species, qtls, search endpoints
│   └── frontend/
│       └── src/
│           ├── App.tsx           # Main layout
│           ├── api/client.ts     # Typed API client
│           ├── hooks/            # useSpecies, useQtlSearch
│           └── components/       # GenomeBrowser, QtlExplorer, SearchBar, etc.
├── scripts/                      # Data pipeline (download, index, convert)
├── tests/                        # 26 backend tests
├── Makefile                      # Orchestration
├── environment.yml               # Conda environment
├── docker-compose.yml            # Production deployment
├── Dockerfile.backend
├── Dockerfile.frontend
└── Dockerfile.data-pipeline      # Data download/indexing container
```

## Development

```bash
# Run tests
make test

# Docker deployment
docker compose up --build
```

## Data Pipeline Notes

- **Ensembl URLs** use `current_gff3` which points to the latest release. If a release bump breaks downloads, update the release number in `scripts/download_annotations.sh`.
- **Animal QTLdb** uses tokenized download URLs that may change with new database releases. If QTL downloads fail, visit the QTLdb index pages and download GFF files manually:
  - Sheep: https://www.animalgenome.org/QTLdb/OA/index
  - Goat: https://www.animalgenome.org/QTLdb/CH/index

---

*Created by Sanad for SOS — April 2026*
