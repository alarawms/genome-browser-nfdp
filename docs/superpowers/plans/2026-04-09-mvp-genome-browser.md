# MVP Saudi Livestock Genome Browser — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a working genome browser for sheep and goat with embedded JBrowse 2, QTL search/filtering, and automated data pipeline.

**Architecture:** Custom React app embedding @jbrowse/react-linear-genome-view, backed by a thin FastAPI service that loads QTL data into pandas DataFrames at startup. Data pipeline scripts download and index genomes from NCBI/Ensembl/Animal QTLdb.

**Tech Stack:** React 18 + TypeScript + Vite, @jbrowse/react-linear-genome-view, Tailwind CSS, FastAPI, pandas, samtools/bgzip/tabix

**Spec:** `docs/superpowers/specs/2026-04-09-mvp-genome-browser-design.md`

---

## Prerequisites

Before starting, install on your workstation:
- Python 3.11+ (`python3 --version`)
- Node 18+ (`node --version`)
- samtools (`samtools --version`) — `conda install -c bioconda samtools` or `brew install samtools`
- htslib (provides bgzip + tabix) — usually bundled with samtools
- Docker + Docker Compose (for final integration)

---

## Task 1: Project Scaffolding & Backend Models

**Files:**
- Create: `src/backend/__init__.py`
- Create: `src/backend/models.py`
- Create: `requirements.txt` (replaces `requirements-backend.txt`)
- Create: `tests/__init__.py`
- Create: `tests/backend/__init__.py`
- Create: `tests/backend/test_models.py`

- [ ] **Step 1: Create backend package structure**

```bash
mkdir -p src/backend/routers tests/backend
touch src/__init__.py src/backend/__init__.py src/backend/routers/__init__.py
touch tests/__init__.py tests/backend/__init__.py
```

- [ ] **Step 2: Write slimmed-down requirements.txt**

Create `requirements.txt`:

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
pydantic==2.9.0
pandas==2.2.0
python-multipart==0.0.9
httpx==0.27.0
pytest==8.3.0
pytest-asyncio==0.24.0
```

- [ ] **Step 3: Create Python venv and install deps**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- [ ] **Step 4: Write failing test for Pydantic models**

Create `tests/backend/test_models.py`:

```python
from src.backend.models import Species, QTL, Trait, SearchResult


def test_species_model():
    s = Species(
        id="sheep",
        name="Sheep",
        scientific_name="Ovis aries",
        assembly="Oar_rambouillet_v1.0",
        chromosome_count=27,
    )
    assert s.id == "sheep"
    assert s.chromosome_count == 27


def test_qtl_model():
    q = QTL(
        id="qtl_001",
        species_id="sheep",
        chromosome="1",
        start=45230100,
        end=47891200,
        trait="Milk yield",
        trait_category="Milk",
        score=4.2,
        pubmed_id="28374882",
        source="Animal QTLdb",
    )
    assert q.chromosome == "1"
    assert q.score == 4.2


def test_trait_model():
    t = Trait(name="Milk yield", category="Milk", qtl_count=47)
    assert t.qtl_count == 47


def test_search_result():
    r = SearchResult(
        type="qtl",
        species_id="sheep",
        label="Milk yield QTL",
        chromosome="1",
        start=45230100,
        end=47891200,
    )
    assert r.type == "qtl"
```

- [ ] **Step 5: Run test — expect FAIL**

```bash
cd /path/to/sheep-qtl
python -m pytest tests/backend/test_models.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.backend.models'`

- [ ] **Step 6: Implement models**

Create `src/backend/models.py`:

```python
from pydantic import BaseModel


class Species(BaseModel):
    id: str
    name: str
    scientific_name: str
    assembly: str
    chromosome_count: int


class QTL(BaseModel):
    id: str
    species_id: str
    chromosome: str
    start: int
    end: int
    trait: str
    trait_category: str
    score: float | None = None
    pubmed_id: str | None = None
    source: str | None = None


class Trait(BaseModel):
    name: str
    category: str
    qtl_count: int


class SearchResult(BaseModel):
    type: str  # "qtl" or "gene"
    species_id: str
    label: str
    chromosome: str
    start: int
    end: int
```

- [ ] **Step 7: Run test — expect PASS**

```bash
python -m pytest tests/backend/test_models.py -v
```

Expected: 4 passed

- [ ] **Step 8: Commit**

```bash
git add src/backend/__init__.py src/backend/models.py src/backend/routers/__init__.py \
       src/__init__.py tests/ requirements.txt
git commit -m "feat: add Pydantic models for Species, QTL, Trait, SearchResult"
```

---

## Task 2: Data Loader

**Files:**
- Create: `src/backend/data_loader.py`
- Create: `tests/backend/test_data_loader.py`
- Create: `tests/fixtures/qtl/sheep/qtls.json`
- Create: `tests/fixtures/qtl/goat/qtls.json`

- [ ] **Step 1: Create test fixture data**

Create `tests/fixtures/qtl/sheep/qtls.json`:

```json
[
  {
    "id": "sheep_qtl_001",
    "species_id": "sheep",
    "chromosome": "1",
    "start": 45230100,
    "end": 47891200,
    "trait": "Milk yield",
    "trait_category": "Milk",
    "score": 4.2,
    "pubmed_id": "28374882",
    "source": "Animal QTLdb"
  },
  {
    "id": "sheep_qtl_002",
    "species_id": "sheep",
    "chromosome": "1",
    "start": 52100300,
    "end": 54200100,
    "trait": "Body weight",
    "trait_category": "Growth",
    "score": 3.8,
    "pubmed_id": "31205743",
    "source": "Animal QTLdb"
  },
  {
    "id": "sheep_qtl_003",
    "species_id": "sheep",
    "chromosome": "3",
    "start": 10500000,
    "end": 12300000,
    "trait": "Wool fiber diameter",
    "trait_category": "Wool",
    "score": 5.1,
    "pubmed_id": "29100001",
    "source": "Animal QTLdb"
  }
]
```

Create `tests/fixtures/qtl/goat/qtls.json`:

```json
[
  {
    "id": "goat_qtl_001",
    "species_id": "goat",
    "chromosome": "5",
    "start": 22000000,
    "end": 24500000,
    "trait": "Milk fat percentage",
    "trait_category": "Milk",
    "score": 3.5,
    "pubmed_id": "30200001",
    "source": "Animal QTLdb"
  },
  {
    "id": "goat_qtl_002",
    "species_id": "goat",
    "chromosome": "5",
    "start": 30000000,
    "end": 32000000,
    "trait": "Cashmere fiber length",
    "trait_category": "Fiber",
    "score": 4.0,
    "pubmed_id": "30200002",
    "source": "Animal QTLdb"
  }
]
```

- [ ] **Step 2: Write failing test for data loader**

Create `tests/backend/test_data_loader.py`:

```python
import os
import pytest
from src.backend.data_loader import DataStore

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")


@pytest.fixture
def store():
    return DataStore(data_dir=FIXTURES_DIR)


def test_load_species_qtls(store):
    sheep_qtls = store.get_qtls("sheep")
    assert len(sheep_qtls) == 3
    assert sheep_qtls[0]["trait"] == "Milk yield"


def test_get_qtls_filtered_by_chromosome(store):
    qtls = store.get_qtls("sheep", chromosome="1")
    assert len(qtls) == 2
    assert all(q["chromosome"] == "1" for q in qtls)


def test_get_qtls_filtered_by_trait_category(store):
    qtls = store.get_qtls("sheep", trait_category="Milk")
    assert len(qtls) == 1
    assert qtls[0]["trait"] == "Milk yield"


def test_get_qtls_filtered_by_region(store):
    qtls = store.get_qtls("sheep", chromosome="1", start=50000000, end=55000000)
    assert len(qtls) == 1
    assert qtls[0]["trait"] == "Body weight"


def test_get_traits(store):
    traits = store.get_traits("sheep")
    categories = {t["category"] for t in traits}
    assert "Milk" in categories
    assert "Growth" in categories
    assert "Wool" in categories


def test_search(store):
    results = store.search("milk")
    assert len(results) >= 1
    assert any("Milk" in r["label"] for r in results)


def test_search_with_species_filter(store):
    results = store.search("milk", species_id="goat")
    assert all(r["species_id"] == "goat" for r in results)


def test_unknown_species_returns_empty(store):
    qtls = store.get_qtls("unknown")
    assert qtls == []
```

- [ ] **Step 3: Run test — expect FAIL**

```bash
python -m pytest tests/backend/test_data_loader.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 4: Implement DataStore**

Create `src/backend/data_loader.py`:

```python
import json
import os
from pathlib import Path

import pandas as pd


class DataStore:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self._qtl_frames: dict[str, pd.DataFrame] = {}
        self._load_all()

    def _load_all(self):
        qtl_dir = self.data_dir / "qtl"
        if not qtl_dir.exists():
            return
        for species_dir in qtl_dir.iterdir():
            if not species_dir.is_dir():
                continue
            json_path = species_dir / "qtls.json"
            if json_path.exists():
                with open(json_path) as f:
                    data = json.load(f)
                if data:
                    self._qtl_frames[species_dir.name] = pd.DataFrame(data)

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
        return result.to_dict(orient="records")

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
        self, query: str, species_id: str | None = None
    ) -> list[dict]:
        results = []
        q = query.lower()
        for sid, df in self._qtl_frames.items():
            if species_id and sid != species_id:
                continue
            matches = df[df["trait"].str.lower().str.contains(q, na=False)]
            for _, row in matches.iterrows():
                results.append(
                    {
                        "type": "qtl",
                        "species_id": sid,
                        "label": f"{row['trait']} QTL",
                        "chromosome": row["chromosome"],
                        "start": int(row["start"]),
                        "end": int(row["end"]),
                    }
                )
        return results
```

- [ ] **Step 5: Run test — expect PASS**

```bash
python -m pytest tests/backend/test_data_loader.py -v
```

Expected: 8 passed

- [ ] **Step 6: Commit**

```bash
git add src/backend/data_loader.py tests/backend/test_data_loader.py tests/fixtures/
git commit -m "feat: add DataStore with pandas-backed QTL loading, filtering, and search"
```

---

## Task 3: JBrowse Config Generator

**Files:**
- Create: `src/backend/jbrowse_config.py`
- Create: `tests/backend/test_jbrowse_config.py`

- [ ] **Step 1: Write failing test**

Create `tests/backend/test_jbrowse_config.py`:

```python
from src.backend.jbrowse_config import make_assembly_config, make_track_configs

BASE_URL = "http://localhost:8000/data"


def test_sheep_assembly_config():
    config = make_assembly_config("sheep", BASE_URL)
    assert config["name"] == "Oar_rambouillet_v1.0"
    assert "sequence" in config
    adapter = config["sequence"]["adapter"]
    assert adapter["type"] == "BgzipFastaAdapter"
    assert "sheep" in adapter["fastaLocation"]["uri"]


def test_goat_assembly_config():
    config = make_assembly_config("goat", BASE_URL)
    assert config["name"] == "CHIR_1.0"


def test_unknown_species_raises():
    import pytest

    with pytest.raises(KeyError):
        make_assembly_config("unknown", BASE_URL)


def test_track_configs():
    tracks = make_track_configs("sheep", BASE_URL)
    track_names = [t["name"] for t in tracks]
    assert "Gene Annotations" in track_names
    assert "QTLs" in track_names


def test_track_adapters():
    tracks = make_track_configs("sheep", BASE_URL)
    gene_track = next(t for t in tracks if t["name"] == "Gene Annotations")
    assert gene_track["adapter"]["type"] == "Gff3TabixAdapter"
    qtl_track = next(t for t in tracks if t["name"] == "QTLs")
    assert qtl_track["adapter"]["type"] == "BedTabixAdapter"
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
python -m pytest tests/backend/test_jbrowse_config.py -v
```

- [ ] **Step 3: Implement jbrowse_config.py**

Create `src/backend/jbrowse_config.py`:

```python
SPECIES_META = {
    "sheep": {
        "assembly_name": "Oar_rambouillet_v1.0",
        "fasta_file": "sheep.fa.gz",
        "gff_file": "sheep.sorted.gff3.gz",
        "qtl_bed_file": "sheep_qtls.sorted.bed.gz",
    },
    "goat": {
        "assembly_name": "CHIR_1.0",
        "fasta_file": "goat.fa.gz",
        "gff_file": "goat.sorted.gff3.gz",
        "qtl_bed_file": "goat_qtls.sorted.bed.gz",
    },
}


def make_assembly_config(species_id: str, base_url: str) -> dict:
    meta = SPECIES_META[species_id]
    genome_url = f"{base_url}/genome/{species_id}"
    return {
        "name": meta["assembly_name"],
        "sequence": {
            "type": "ReferenceSequenceTrack",
            "trackId": f"{species_id}-reference",
            "adapter": {
                "type": "BgzipFastaAdapter",
                "fastaLocation": {"uri": f"{genome_url}/{meta['fasta_file']}"},
                "faiLocation": {"uri": f"{genome_url}/{meta['fasta_file']}.fai"},
                "gziLocation": {"uri": f"{genome_url}/{meta['fasta_file']}.gzi"},
            },
        },
    }


def make_track_configs(species_id: str, base_url: str) -> list[dict]:
    meta = SPECIES_META[species_id]
    ann_url = f"{base_url}/annotations/{species_id}"
    qtl_url = f"{base_url}/qtl/{species_id}"
    assembly_name = meta["assembly_name"]
    return [
        {
            "type": "FeatureTrack",
            "trackId": f"{species_id}-genes",
            "name": "Gene Annotations",
            "assemblyNames": [assembly_name],
            "adapter": {
                "type": "Gff3TabixAdapter",
                "gffGzLocation": {"uri": f"{ann_url}/{meta['gff_file']}"},
                "index": {
                    "location": {"uri": f"{ann_url}/{meta['gff_file']}.tbi"},
                },
            },
        },
        {
            "type": "FeatureTrack",
            "trackId": f"{species_id}-qtls",
            "name": "QTLs",
            "assemblyNames": [assembly_name],
            "adapter": {
                "type": "BedTabixAdapter",
                "bedGzLocation": {"uri": f"{qtl_url}/{meta['qtl_bed_file']}"},
                "index": {
                    "location": {
                        "uri": f"{qtl_url}/{meta['qtl_bed_file']}.tbi"
                    },
                },
            },
        },
    ]
```

- [ ] **Step 4: Run test — expect PASS**

```bash
python -m pytest tests/backend/test_jbrowse_config.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/backend/jbrowse_config.py tests/backend/test_jbrowse_config.py
git commit -m "feat: add JBrowse 2 assembly and track config generator"
```

---

## Task 4: FastAPI Application & Routers

**Files:**
- Create: `src/backend/main.py`
- Create: `src/backend/routers/species.py`
- Create: `src/backend/routers/qtls.py`
- Create: `src/backend/routers/search.py`
- Create: `tests/backend/test_api.py`

- [ ] **Step 1: Write failing API test**

Create `tests/backend/test_api.py`:

```python
import os
import pytest
from fastapi.testclient import TestClient

os.environ["DATA_DIR"] = os.path.join(os.path.dirname(__file__), "..", "fixtures")

from src.backend.main import app

client = TestClient(app)


def test_list_species():
    resp = client.get("/api/species")
    assert resp.status_code == 200
    species = resp.json()
    assert len(species) == 2
    ids = {s["id"] for s in species}
    assert "sheep" in ids
    assert "goat" in ids


def test_get_qtls():
    resp = client.get("/api/species/sheep/qtls")
    assert resp.status_code == 200
    qtls = resp.json()
    assert len(qtls) == 3


def test_get_qtls_with_chromosome_filter():
    resp = client.get("/api/species/sheep/qtls?chromosome=1")
    assert resp.status_code == 200
    qtls = resp.json()
    assert len(qtls) == 2


def test_get_qtls_with_trait_filter():
    resp = client.get("/api/species/sheep/qtls?trait_category=Milk")
    assert resp.status_code == 200
    qtls = resp.json()
    assert len(qtls) == 1


def test_get_traits():
    resp = client.get("/api/species/sheep/traits")
    assert resp.status_code == 200
    traits = resp.json()
    categories = {t["category"] for t in traits}
    assert "Milk" in categories


def test_search():
    resp = client.get("/api/search?q=milk")
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) >= 1


def test_search_with_species():
    resp = client.get("/api/search?q=milk&species=goat")
    assert resp.status_code == 200
    results = resp.json()
    assert all(r["species_id"] == "goat" for r in results)


def test_jbrowse_config():
    resp = client.get("/api/species/sheep/jbrowse-config")
    assert resp.status_code == 200
    config = resp.json()
    assert "assembly" in config
    assert "tracks" in config
    assert config["assembly"]["name"] == "Oar_rambouillet_v1.0"


def test_unknown_species_404():
    resp = client.get("/api/species/unknown/qtls")
    assert resp.status_code == 200
    assert resp.json() == []
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
python -m pytest tests/backend/test_api.py -v
```

- [ ] **Step 3: Implement routers/species.py**

Create `src/backend/routers/species.py`:

```python
from fastapi import APIRouter, Request

from src.backend.jbrowse_config import make_assembly_config, make_track_configs
from src.backend.models import Species

router = APIRouter(prefix="/api/species", tags=["species"])

SPECIES_INFO = [
    Species(
        id="sheep",
        name="Sheep",
        scientific_name="Ovis aries",
        assembly="Oar_rambouillet_v1.0",
        chromosome_count=27,
    ),
    Species(
        id="goat",
        name="Goat",
        scientific_name="Capra hircus",
        assembly="CHIR_1.0",
        chromosome_count=30,
    ),
]


@router.get("")
def list_species() -> list[Species]:
    return SPECIES_INFO


@router.get("/{species_id}/jbrowse-config")
def jbrowse_config(species_id: str, request: Request):
    base_url = str(request.base_url).rstrip("/") + "/data"
    assembly = make_assembly_config(species_id, base_url)
    tracks = make_track_configs(species_id, base_url)
    return {"assembly": assembly, "tracks": tracks}
```

- [ ] **Step 4: Implement routers/qtls.py**

Create `src/backend/routers/qtls.py`:

```python
from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/species/{species_id}", tags=["qtls"])


@router.get("/qtls")
def get_qtls(
    species_id: str,
    request: Request,
    chromosome: str | None = None,
    start: int | None = None,
    end: int | None = None,
    trait_category: str | None = None,
    min_score: float | None = None,
    limit: int = 100,
    offset: int = 0,
):
    store = request.app.state.store
    return store.get_qtls(
        species_id,
        chromosome=chromosome,
        start=start,
        end=end,
        trait_category=trait_category,
        min_score=min_score,
        limit=limit,
        offset=offset,
    )


@router.get("/traits")
def get_traits(species_id: str, request: Request):
    store = request.app.state.store
    return store.get_traits(species_id)
```

- [ ] **Step 5: Implement routers/search.py**

Create `src/backend/routers/search.py`:

```python
from fastapi import APIRouter, Request

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search")
def search(q: str, request: Request, species: str | None = None):
    store = request.app.state.store
    return store.search(q, species_id=species)
```

- [ ] **Step 6: Implement main.py**

Create `src/backend/main.py`:

```python
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.backend.data_loader import DataStore
from src.backend.routers import species, qtls, search

DATA_DIR = os.environ.get("DATA_DIR", "data")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.store = DataStore(data_dir=DATA_DIR)
    yield


app = FastAPI(title="Saudi Livestock Genome Browser API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(species.router)
app.include_router(qtls.router)
app.include_router(search.router)

# Mount data directory for JBrowse 2 static file access
data_path = os.path.abspath(DATA_DIR)
if os.path.isdir(data_path):
    app.mount("/data", StaticFiles(directory=data_path), name="data")
```

- [ ] **Step 7: Run tests — expect PASS**

```bash
python -m pytest tests/backend/ -v
```

Expected: All 17 tests pass (4 models + 8 data_loader + 5 jbrowse_config + ... wait, let me recount the API tests: 9 API tests). Total: 4 + 8 + 5 + 9 = 26 tests.

- [ ] **Step 8: Commit**

```bash
git add src/backend/main.py src/backend/routers/ tests/backend/test_api.py
git commit -m "feat: add FastAPI app with species, QTL, search, and JBrowse config endpoints"
```

---

## Task 5: Data Pipeline Scripts

**Files:**
- Create: `scripts/download_genomes.sh`
- Create: `scripts/download_annotations.sh`
- Create: `scripts/download_qtls.sh`
- Create: `scripts/index_genomes.sh`
- Create: `scripts/prepare_tracks.sh`
- Create: `scripts/convert_qtl_to_bed.py`
- Create: `Makefile`

- [ ] **Step 1: Create download_genomes.sh**

Create `scripts/download_genomes.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${1:-data}"

download_genome() {
    local species="$1" url="$2" filename="$3"
    local outdir="$DATA_DIR/genome/$species"
    local outfile="$outdir/$filename"

    mkdir -p "$outdir"
    if [ -f "$outfile" ]; then
        echo "  ✓ $outfile already exists, skipping"
        return
    fi
    echo "  Downloading $species genome..."
    curl -L -o "$outfile.gz" "$url"
    gunzip "$outfile.gz"
    echo "  ✓ $outfile"
}

echo "=== Downloading reference genomes ==="

# Sheep — Oar_rambouillet_v1.0
download_genome "sheep" \
    "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/002/742/125/GCF_002742125.1_Oar_rambouillet_v1.0/GCF_002742125.1_Oar_rambouillet_v1.0_genomic.fna.gz" \
    "sheep.fa"

# Goat — ARS1 / CHIR_1.0
download_genome "goat" \
    "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/001/704/415/GCF_001704415.2_ARS1.2/GCF_001704415.2_ARS1.2_genomic.fna.gz" \
    "goat.fa"

echo "=== Genome downloads complete ==="
```

- [ ] **Step 2: Create download_annotations.sh**

Create `scripts/download_annotations.sh`:

```bash
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
```

- [ ] **Step 3: Create download_qtls.sh**

Create `scripts/download_qtls.sh`:

```bash
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
    curl -L -o "$outfile" "$url"
    echo "  ✓ $outfile"
}

echo "=== Downloading QTL data from Animal QTLdb ==="

# Sheep QTLs — GFF format from Animal QTLdb
download_qtl "sheep" \
    "https://www.animalgenome.org/cgi-bin/QTLdb/OA/downloaddatfile?TYPE=gff&FILEID=1" \
    "sheep_qtldb.gff"

# Goat QTLs — GFF format from Animal QTLdb
download_qtl "goat" \
    "https://www.animalgenome.org/cgi-bin/QTLdb/CH/downloaddatfile?TYPE=gff&FILEID=1" \
    "goat_qtldb.gff"

echo "=== QTL downloads complete ==="
```

- [ ] **Step 4: Create convert_qtl_to_bed.py**

Create `scripts/convert_qtl_to_bed.py`:

```python
#!/usr/bin/env python3
"""Convert Animal QTLdb GFF files to BED format and JSON for the backend."""
import json
import re
import sys
from pathlib import Path


def parse_qtldb_gff(gff_path: Path, species_id: str) -> list[dict]:
    """Parse Animal QTLdb GFF file into structured records."""
    records = []
    with open(gff_path) as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            if len(parts) < 9:
                continue

            chrom = parts[0]
            start = int(parts[3]) - 1  # GFF is 1-based, BED is 0-based
            end = int(parts[4])
            score_str = parts[5]
            attrs_str = parts[8]

            # Parse attributes
            attrs = {}
            for attr in attrs_str.split(";"):
                attr = attr.strip()
                if "=" in attr:
                    key, val = attr.split("=", 1)
                    attrs[key] = val

            # Extract trait info
            trait_name = attrs.get("Name", attrs.get("QTL_type", "Unknown"))
            trait_name = trait_name.replace("_", " ").replace("%20", " ")

            # Categorize trait
            trait_category = categorize_trait(trait_name)

            score = None
            if score_str != ".":
                try:
                    score = float(score_str)
                except ValueError:
                    pass

            pubmed_id = attrs.get("PUBMED_ID", attrs.get("Pubmed_id", None))

            # Normalize chromosome name — strip "chr" prefix if present
            chrom = re.sub(r"^chr", "", chrom, flags=re.IGNORECASE)

            qtl_id = f"{species_id}_qtl_{len(records):06d}"
            records.append(
                {
                    "id": qtl_id,
                    "species_id": species_id,
                    "chromosome": chrom,
                    "start": max(0, start),
                    "end": end,
                    "trait": trait_name,
                    "trait_category": trait_category,
                    "score": score,
                    "pubmed_id": pubmed_id,
                    "source": "Animal QTLdb",
                }
            )
    return records


def categorize_trait(trait_name: str) -> str:
    """Assign a trait category based on the trait name."""
    name = trait_name.lower()
    if any(kw in name for kw in ["milk", "lactation", "dairy", "casein"]):
        return "Milk"
    if any(kw in name for kw in ["meat", "carcass", "muscle", "tenderness"]):
        return "Meat"
    if any(kw in name for kw in ["wool", "fiber", "fleece", "cashmere"]):
        return "Wool/Fiber"
    if any(kw in name for kw in ["disease", "resistance", "immune", "parasite", "health"]):
        return "Disease Resistance"
    if any(kw in name for kw in ["fertility", "reproduction", "litter", "ovulation", "twinning"]):
        return "Reproduction"
    if any(kw in name for kw in ["weight", "growth", "body", "height", "size"]):
        return "Growth"
    return "Other"


def write_bed(records: list[dict], bed_path: Path):
    """Write records as BED format (chrom, start, end, name, score)."""
    with open(bed_path, "w") as f:
        for r in sorted(records, key=lambda x: (x["chromosome"], x["start"])):
            score = int(r["score"]) if r["score"] is not None else 0
            name = r["trait"].replace(" ", "_")[:50]
            f.write(f"{r['chromosome']}\t{r['start']}\t{r['end']}\t{name}\t{score}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: convert_qtl_to_bed.py <data_dir>")
        sys.exit(1)

    data_dir = Path(sys.argv[1])

    for species_id in ["sheep", "goat"]:
        gff_path = data_dir / "qtl" / species_id / f"{species_id}_qtldb.gff"
        if not gff_path.exists():
            print(f"  ⚠ {gff_path} not found, skipping {species_id}")
            continue

        print(f"  Converting {species_id} QTLs...")
        records = parse_qtldb_gff(gff_path, species_id)
        print(f"    Parsed {len(records)} QTLs")

        # Write JSON for backend
        json_path = data_dir / "qtl" / species_id / "qtls.json"
        with open(json_path, "w") as f:
            json.dump(records, f, indent=2)
        print(f"    ✓ {json_path}")

        # Write BED for JBrowse 2
        bed_path = data_dir / "qtl" / species_id / f"{species_id}_qtls.bed"
        write_bed(records, bed_path)
        print(f"    ✓ {bed_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Create index_genomes.sh**

Create `scripts/index_genomes.sh`:

```bash
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
```

- [ ] **Step 6: Create prepare_tracks.sh**

Create `scripts/prepare_tracks.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${1:-data}"

prepare_gff() {
    local species="$1"
    local infile="$DATA_DIR/annotations/$species/$species.gff3.gz"
    local sorted="$DATA_DIR/annotations/$species/$species.sorted.gff3.gz"

    if [ ! -f "$infile" ]; then
        echo "  ⚠ $infile not found, skipping"
        return
    fi
    if [ -f "$sorted.tbi" ]; then
        echo "  ✓ $sorted already indexed"
        return
    fi

    echo "  Sorting and indexing $species GFF3..."
    # Decompress, sort, recompress, index
    zcat "$infile" | grep -v "^#" | sort -k1,1 -k4,4n | bgzip > "$sorted"
    tabix -p gff "$sorted"
    echo "  ✓ $sorted + .tbi"
}

prepare_bed() {
    local species="$1"
    local infile="$DATA_DIR/qtl/$species/${species}_qtls.bed"
    local sorted="$DATA_DIR/qtl/$species/${species}_qtls.sorted.bed.gz"

    if [ ! -f "$infile" ]; then
        echo "  ⚠ $infile not found, skipping"
        return
    fi
    if [ -f "$sorted.tbi" ]; then
        echo "  ✓ $sorted already indexed"
        return
    fi

    echo "  Sorting and indexing $species QTL BED..."
    sort -k1,1 -k2,2n "$infile" | bgzip > "$sorted"
    tabix -p bed "$sorted"
    echo "  ✓ $sorted + .tbi"
}

echo "=== Preparing track files for JBrowse 2 ==="
for species in sheep goat; do
    prepare_gff "$species"
    prepare_bed "$species"
done
echo "=== Track preparation complete ==="
```

- [ ] **Step 7: Create Makefile**

Create `Makefile`:

```makefile
DATA_DIR ?= data

.PHONY: data download-genomes download-annotations download-qtls \
        index-genomes convert-qtls prepare-tracks \
        dev-backend dev-frontend dev clean

## === Data Pipeline ===

data: download-genomes download-annotations download-qtls index-genomes convert-qtls prepare-tracks
	@echo "✓ All data ready"

download-genomes:
	bash scripts/download_genomes.sh $(DATA_DIR)

download-annotations:
	bash scripts/download_annotations.sh $(DATA_DIR)

download-qtls:
	bash scripts/download_qtls.sh $(DATA_DIR)

index-genomes: download-genomes
	bash scripts/index_genomes.sh $(DATA_DIR)

convert-qtls: download-qtls
	python3 scripts/convert_qtl_to_bed.py $(DATA_DIR)

prepare-tracks: download-annotations convert-qtls
	bash scripts/prepare_tracks.sh $(DATA_DIR)

## === Development ===

dev-backend:
	cd src/backend && DATA_DIR=../../$(DATA_DIR) python -m uvicorn main:app --reload --port 8000

dev-frontend:
	cd src/frontend && npm run dev

dev:
	@echo "Run in two terminals:"
	@echo "  make dev-backend"
	@echo "  make dev-frontend"

## === Testing ===

test:
	python -m pytest tests/ -v

## === Cleanup ===

clean:
	rm -rf $(DATA_DIR)/genome $(DATA_DIR)/annotations $(DATA_DIR)/qtl
```

- [ ] **Step 8: Make scripts executable and commit**

```bash
chmod +x scripts/*.sh scripts/*.py
git add scripts/ Makefile
git commit -m "feat: add data pipeline scripts and Makefile orchestration"
```

---

## Task 6: Frontend Scaffolding

**Files:**
- Create: `src/frontend/package.json`
- Create: `src/frontend/vite.config.ts`
- Create: `src/frontend/tsconfig.json`
- Create: `src/frontend/tsconfig.node.json`
- Create: `src/frontend/index.html`
- Create: `src/frontend/src/main.tsx`
- Create: `src/frontend/src/index.css`
- Create: `src/frontend/tailwind.config.js`
- Create: `src/frontend/postcss.config.js`

- [ ] **Step 1: Create package.json**

Create `src/frontend/package.json`:

```json
{
  "name": "saudi-livestock-genome-browser",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@jbrowse/core": "^2.18.0",
    "@jbrowse/plugin-linear-genome-view": "^2.18.0",
    "@jbrowse/react-linear-genome-view": "^2.18.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0"
  }
}
```

- [ ] **Step 2: Create vite.config.ts**

Create `src/frontend/vite.config.ts`:

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api": "http://localhost:8000",
      "/data": "http://localhost:8000",
    },
  },
});
```

- [ ] **Step 3: Create tsconfig.json**

Create `src/frontend/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"]
}
```

- [ ] **Step 4: Create Tailwind + PostCSS config**

Create `src/frontend/tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: { extend: {} },
  plugins: [],
};
```

Create `src/frontend/postcss.config.js`:

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

- [ ] **Step 5: Create index.html and entry point**

Create `src/frontend/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Saudi Livestock Genome Browser</title>
  </head>
  <body class="bg-gray-950 text-gray-100">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

Create `src/frontend/src/main.tsx`:

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

Create `src/frontend/src/index.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 6: Install dependencies**

```bash
cd src/frontend && npm install
```

- [ ] **Step 7: Commit**

```bash
git add src/frontend/package.json src/frontend/vite.config.ts \
       src/frontend/tsconfig.json src/frontend/tailwind.config.js \
       src/frontend/postcss.config.js src/frontend/index.html \
       src/frontend/src/main.tsx src/frontend/src/index.css
git commit -m "feat: scaffold React + Vite + Tailwind frontend with JBrowse 2 deps"
```

---

## Task 7: API Client & Hooks

**Files:**
- Create: `src/frontend/src/api/client.ts`
- Create: `src/frontend/src/hooks/useSpecies.ts`
- Create: `src/frontend/src/hooks/useQtlSearch.ts`

- [ ] **Step 1: Create API client**

Create `src/frontend/src/api/client.ts`:

```typescript
const BASE = "";

export interface Species {
  id: string;
  name: string;
  scientific_name: string;
  assembly: string;
  chromosome_count: number;
}

export interface QTL {
  id: string;
  species_id: string;
  chromosome: string;
  start: number;
  end: number;
  trait: string;
  trait_category: string;
  score: number | null;
  pubmed_id: string | null;
  source: string | null;
}

export interface Trait {
  name: string;
  category: string;
  qtl_count: number;
}

export interface SearchResult {
  type: string;
  species_id: string;
  label: string;
  chromosome: string;
  start: number;
  end: number;
}

export interface JBrowseConfig {
  assembly: Record<string, unknown>;
  tracks: Record<string, unknown>[];
}

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  getSpecies: () => fetchJson<Species[]>("/api/species"),

  getQtls: (speciesId: string, params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return fetchJson<QTL[]>(`/api/species/${speciesId}/qtls${qs}`);
  },

  getTraits: (speciesId: string) =>
    fetchJson<Trait[]>(`/api/species/${speciesId}/traits`),

  search: (query: string, species?: string) => {
    const params = new URLSearchParams({ q: query });
    if (species) params.set("species", species);
    return fetchJson<SearchResult[]>(`/api/search?${params}`);
  },

  getJBrowseConfig: (speciesId: string) =>
    fetchJson<JBrowseConfig>(`/api/species/${speciesId}/jbrowse-config`),
};
```

- [ ] **Step 2: Create useSpecies hook**

Create `src/frontend/src/hooks/useSpecies.ts`:

```typescript
import { useCallback, useEffect, useState } from "react";
import { api, Species } from "../api/client";

export function useSpecies() {
  const [species, setSpecies] = useState<Species[]>([]);
  const [selectedId, setSelectedId] = useState<string>("sheep");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSpecies().then((data) => {
      setSpecies(data);
      setLoading(false);
    });
  }, []);

  const selected = species.find((s) => s.id === selectedId) ?? null;

  const select = useCallback((id: string) => setSelectedId(id), []);

  return { species, selected, selectedId, select, loading };
}
```

- [ ] **Step 3: Create useQtlSearch hook**

Create `src/frontend/src/hooks/useQtlSearch.ts`:

```typescript
import { useEffect, useRef, useState } from "react";
import { api, QTL, Trait } from "../api/client";

interface Filters {
  chromosome?: string;
  traitCategory?: string;
}

export function useQtlSearch(speciesId: string) {
  const [qtls, setQtls] = useState<QTL[]>([]);
  const [traits, setTraits] = useState<Trait[]>([]);
  const [filters, setFilters] = useState<Filters>({});
  const [loading, setLoading] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  // Fetch traits when species changes
  useEffect(() => {
    api.getTraits(speciesId).then(setTraits);
  }, [speciesId]);

  // Fetch QTLs when species or filters change (debounced)
  useEffect(() => {
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setLoading(true);
      const params: Record<string, string> = {};
      if (filters.chromosome) params.chromosome = filters.chromosome;
      if (filters.traitCategory) params.trait_category = filters.traitCategory;
      api.getQtls(speciesId, params).then((data) => {
        setQtls(data);
        setLoading(false);
      });
    }, 200);
    return () => clearTimeout(debounceRef.current);
  }, [speciesId, filters]);

  return { qtls, traits, filters, setFilters, loading };
}
```

- [ ] **Step 4: Commit**

```bash
git add src/frontend/src/api/ src/frontend/src/hooks/
git commit -m "feat: add API client and React hooks for species and QTL data"
```

---

## Task 8: React Components — App Shell & Species Selector

**Files:**
- Create: `src/frontend/src/App.tsx`
- Create: `src/frontend/src/components/SpeciesSelector.tsx`

- [ ] **Step 1: Create SpeciesSelector**

Create `src/frontend/src/components/SpeciesSelector.tsx`:

```tsx
import { Species } from "../api/client";

interface Props {
  species: Species[];
  selectedId: string;
  onSelect: (id: string) => void;
}

export default function SpeciesSelector({ species, selectedId, onSelect }: Props) {
  return (
    <div className="flex gap-1 rounded-lg border border-blue-500/30 bg-gray-800 p-1">
      {species.map((s) => (
        <button
          key={s.id}
          onClick={() => onSelect(s.id)}
          className={`rounded-md px-3 py-1 text-sm font-medium transition-colors ${
            s.id === selectedId
              ? "bg-blue-600 text-white"
              : "text-gray-400 hover:text-white"
          }`}
        >
          {s.name}
        </button>
      ))}
    </div>
  );
}
```

- [ ] **Step 2: Create App.tsx**

Create `src/frontend/src/App.tsx`:

```tsx
import { useState } from "react";
import { useSpecies } from "./hooks/useSpecies";
import SpeciesSelector from "./components/SpeciesSelector";
import QtlExplorer from "./components/QtlExplorer";
import GenomeBrowser from "./components/GenomeBrowser";
import SearchBar from "./components/SearchBar";

export default function App() {
  const { species, selectedId, select, loading } = useSpecies();
  const [location, setLocation] = useState<{
    chromosome: string;
    start: number;
    end: number;
  } | null>(null);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p className="text-gray-400">Loading...</p>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-gray-800 bg-gray-900 px-4 py-3">
        <h1 className="text-lg font-bold text-emerald-400">
          🧬 Saudi Livestock Genome Browser
        </h1>
        <div className="flex items-center gap-4">
          <SpeciesSelector
            species={species}
            selectedId={selectedId}
            onSelect={select}
          />
          <SearchBar
            speciesId={selectedId}
            onNavigate={(chr, start, end) =>
              setLocation({ chromosome: chr, start, end })
            }
          />
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-72 overflow-y-auto border-r border-gray-800 bg-gray-900">
          <QtlExplorer
            speciesId={selectedId}
            onQtlClick={(chr, start, end) =>
              setLocation({ chromosome: chr, start, end })
            }
          />
        </aside>

        {/* Genome Browser */}
        <main className="flex-1">
          <GenomeBrowser speciesId={selectedId} location={location} />
        </main>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/App.tsx src/frontend/src/components/SpeciesSelector.tsx
git commit -m "feat: add App shell with header, species selector, and layout"
```

---

## Task 9: React Components — QTL Explorer & Detail

**Files:**
- Create: `src/frontend/src/components/QtlExplorer.tsx`
- Create: `src/frontend/src/components/QtlDetail.tsx`

- [ ] **Step 1: Create QtlDetail**

Create `src/frontend/src/components/QtlDetail.tsx`:

```tsx
import { QTL } from "../api/client";

interface Props {
  qtl: QTL;
  onNavigate: (chr: string, start: number, end: number) => void;
}

export default function QtlDetail({ qtl, onNavigate }: Props) {
  return (
    <button
      onClick={() => onNavigate(qtl.chromosome, qtl.start, qtl.end)}
      className="w-full rounded-md bg-gray-800 p-3 text-left transition-colors hover:bg-gray-750 border-l-[3px]"
      style={{
        borderLeftColor: categoryColor(qtl.trait_category),
      }}
    >
      <p className="text-sm font-semibold text-white">{qtl.trait}</p>
      <p className="mt-1 text-xs text-gray-400">
        Chr{qtl.chromosome}:{qtl.start.toLocaleString()}-{qtl.end.toLocaleString()}
      </p>
      <div className="mt-1 flex items-center gap-2 text-xs">
        {qtl.score != null && (
          <span style={{ color: categoryColor(qtl.trait_category) }}>
            Score: {qtl.score}
          </span>
        )}
        {qtl.pubmed_id && (
          <a
            href={`https://pubmed.ncbi.nlm.nih.gov/${qtl.pubmed_id}/`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 hover:underline"
            onClick={(e) => e.stopPropagation()}
          >
            PMID:{qtl.pubmed_id}
          </a>
        )}
      </div>
    </button>
  );
}

function categoryColor(category: string): string {
  const colors: Record<string, string> = {
    Milk: "#4ade80",
    Meat: "#f87171",
    "Wool/Fiber": "#c084fc",
    "Disease Resistance": "#38bdf8",
    Reproduction: "#fb923c",
    Growth: "#facc15",
    Other: "#94a3b8",
  };
  return colors[category] ?? colors.Other;
}
```

- [ ] **Step 2: Create QtlExplorer**

Create `src/frontend/src/components/QtlExplorer.tsx`:

```tsx
import { useQtlSearch } from "../hooks/useQtlSearch";
import QtlDetail from "./QtlDetail";

interface Props {
  speciesId: string;
  onQtlClick: (chr: string, start: number, end: number) => void;
}

const CHROMOSOMES = [
  ...Array.from({ length: 26 }, (_, i) => String(i + 1)),
  "X",
];

export default function QtlExplorer({ speciesId, onQtlClick }: Props) {
  const { qtls, traits, filters, setFilters, loading } =
    useQtlSearch(speciesId);

  return (
    <div className="flex flex-col gap-4 p-4">
      <h2 className="text-sm font-bold text-amber-400">QTL Explorer</h2>

      {/* Chromosome picker */}
      <div>
        <p className="mb-2 text-xs uppercase text-gray-500">Chromosome</p>
        <div className="flex flex-wrap gap-1">
          <button
            onClick={() => setFilters((f) => ({ ...f, chromosome: undefined }))}
            className={`rounded px-2 py-0.5 text-xs ${
              !filters.chromosome
                ? "bg-blue-600 text-white"
                : "bg-gray-800 text-gray-400 hover:text-white"
            }`}
          >
            All
          </button>
          {CHROMOSOMES.map((chr) => (
            <button
              key={chr}
              onClick={() => setFilters((f) => ({ ...f, chromosome: chr }))}
              className={`rounded px-2 py-0.5 text-xs ${
                filters.chromosome === chr
                  ? "bg-blue-600 text-white"
                  : "bg-gray-800 text-gray-400 hover:text-white"
              }`}
            >
              {chr}
            </button>
          ))}
        </div>
      </div>

      {/* Trait category filter */}
      <div>
        <p className="mb-2 text-xs uppercase text-gray-500">Trait Category</p>
        <div className="flex flex-col gap-1">
          <button
            onClick={() =>
              setFilters((f) => ({ ...f, traitCategory: undefined }))
            }
            className={`text-left text-xs ${
              !filters.traitCategory ? "text-emerald-400" : "text-gray-400"
            }`}
          >
            {!filters.traitCategory ? "☑" : "☐"} All categories
          </button>
          {traits.map((t) => (
            <button
              key={t.category}
              onClick={() =>
                setFilters((f) => ({
                  ...f,
                  traitCategory:
                    f.traitCategory === t.category ? undefined : t.category,
                }))
              }
              className={`text-left text-xs ${
                filters.traitCategory === t.category
                  ? "text-emerald-400"
                  : "text-gray-400"
              }`}
            >
              {filters.traitCategory === t.category ? "☑" : "☐"} {t.category} (
              {t.qtl_count})
            </button>
          ))}
        </div>
      </div>

      {/* Results */}
      <div>
        <p className="mb-2 text-xs uppercase text-gray-500">
          Results ({loading ? "..." : qtls.length} QTLs)
        </p>
        <div className="flex flex-col gap-2">
          {qtls.map((qtl) => (
            <QtlDetail key={qtl.id} qtl={qtl} onNavigate={onQtlClick} />
          ))}
          {!loading && qtls.length === 0 && (
            <p className="text-xs text-gray-500">No QTLs match filters</p>
          )}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/components/QtlExplorer.tsx src/frontend/src/components/QtlDetail.tsx
git commit -m "feat: add QTL explorer sidebar with chromosome/trait filtering"
```

---

## Task 10: React Components — Search Bar

**Files:**
- Create: `src/frontend/src/components/SearchBar.tsx`

- [ ] **Step 1: Create SearchBar**

Create `src/frontend/src/components/SearchBar.tsx`:

```tsx
import { useRef, useState } from "react";
import { api, SearchResult } from "../api/client";

interface Props {
  speciesId: string;
  onNavigate: (chr: string, start: number, end: number) => void;
}

export default function SearchBar({ speciesId, onNavigate }: Props) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [open, setOpen] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  function handleChange(value: string) {
    setQuery(value);
    clearTimeout(debounceRef.current);
    if (value.length < 2) {
      setResults([]);
      setOpen(false);
      return;
    }
    debounceRef.current = setTimeout(() => {
      api.search(value, speciesId).then((r) => {
        setResults(r.slice(0, 10));
        setOpen(true);
      });
    }, 300);
  }

  function handleSelect(r: SearchResult) {
    onNavigate(r.chromosome, r.start, r.end);
    setOpen(false);
    setQuery("");
  }

  return (
    <div className="relative">
      <input
        type="text"
        value={query}
        onChange={(e) => handleChange(e.target.value)}
        onFocus={() => results.length > 0 && setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 200)}
        placeholder="Search genes, QTLs, traits..."
        className="w-56 rounded-lg border border-gray-600 bg-gray-800 px-3 py-1.5 text-sm text-gray-200 placeholder-gray-500 focus:border-blue-500 focus:outline-none"
      />
      {open && results.length > 0 && (
        <div className="absolute right-0 top-full z-50 mt-1 w-80 rounded-lg border border-gray-700 bg-gray-800 shadow-xl">
          {results.map((r, i) => (
            <button
              key={i}
              onMouseDown={() => handleSelect(r)}
              className="flex w-full flex-col px-3 py-2 text-left hover:bg-gray-700"
            >
              <span className="text-sm text-white">{r.label}</span>
              <span className="text-xs text-gray-400">
                Chr{r.chromosome}:{r.start.toLocaleString()}-
                {r.end.toLocaleString()} ({r.species_id})
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add src/frontend/src/components/SearchBar.tsx
git commit -m "feat: add search bar with debounced API search and dropdown results"
```

---

## Task 11: React Components — Genome Browser (JBrowse 2 Integration)

**Files:**
- Create: `src/frontend/src/components/GenomeBrowser.tsx`

This is the core integration. The `@jbrowse/react-linear-genome-view` package provides a `createViewState` factory and a `JBrowseLinearGenomeView` React component.

- [ ] **Step 1: Create GenomeBrowser**

Create `src/frontend/src/components/GenomeBrowser.tsx`:

```tsx
import { useEffect, useRef, useState } from "react";
import { createViewState, JBrowseLinearGenomeView } from "@jbrowse/react-linear-genome-view";
import { api } from "../api/client";

interface Props {
  speciesId: string;
  location: { chromosome: string; start: number; end: number } | null;
}

export default function GenomeBrowser({ speciesId, location }: Props) {
  const [viewState, setViewState] = useState<ReturnType<typeof createViewState> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const prevSpecies = useRef(speciesId);

  // Load JBrowse config when species changes
  useEffect(() => {
    let cancelled = false;
    setError(null);

    api.getJBrowseConfig(speciesId).then((config) => {
      if (cancelled) return;
      try {
        const state = createViewState({
          assembly: config.assembly as any,
          tracks: config.tracks as any[],
          defaultSession: {
            name: "default",
            view: {
              id: "linearGenomeView",
              type: "LinearGenomeView",
              tracks: config.tracks.map((t: any) => ({
                type: "FeatureTrack",
                configuration: t.trackId,
                displays: [
                  {
                    type: "LinearBasicDisplay",
                    configuration: `${t.trackId}-LinearBasicDisplay`,
                  },
                ],
              })),
            },
          },
        });
        setViewState(state);
        prevSpecies.current = speciesId;
      } catch (e) {
        setError(`Failed to initialize genome view: ${e}`);
      }
    }).catch((e) => {
      if (!cancelled) setError(`Failed to load config: ${e.message}`);
    });

    return () => { cancelled = true; };
  }, [speciesId]);

  // Navigate when location changes
  useEffect(() => {
    if (!viewState || !location) return;
    try {
      viewState.session.view.navToLocString(
        `${location.chromosome}:${location.start}-${location.end}`,
      );
    } catch {
      // Location string may not match assembly — ignore
    }
  }, [viewState, location]);

  if (error) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="rounded-lg bg-red-900/30 p-6 text-center">
          <p className="text-red-400">{error}</p>
          <p className="mt-2 text-sm text-gray-400">
            Make sure the backend is running and data is loaded (run `make data`)
          </p>
        </div>
      </div>
    );
  }

  if (!viewState) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-gray-400">Loading genome browser...</p>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto bg-white">
      <JBrowseLinearGenomeView viewState={viewState} />
    </div>
  );
}
```

- [ ] **Step 2: Verify frontend compiles**

```bash
cd src/frontend && npx tsc --noEmit
```

Fix any type errors. The JBrowse 2 types can be loose — `as any` casts are acceptable for the config objects.

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/components/GenomeBrowser.tsx
git commit -m "feat: add JBrowse 2 genome browser component with species switching and navigation"
```

---

## Task 12: Docker Configuration

**Files:**
- Modify: `docker-compose.yml`
- Modify: `Dockerfile.backend`
- Modify: `Dockerfile.frontend`

- [ ] **Step 1: Update docker-compose.yml**

Overwrite `docker-compose.yml`:

```yaml
version: "3.8"

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data:ro
    environment:
      - DATA_DIR=/app/data

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

- [ ] **Step 2: Update Dockerfile.backend**

Overwrite `Dockerfile.backend`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/backend/ ./src/backend/
COPY src/__init__.py ./src/

ENV DATA_DIR=/app/data

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s \
  CMD curl -f http://localhost:8000/api/species || exit 1

CMD ["python", "-m", "uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 3: Update Dockerfile.frontend**

Overwrite `Dockerfile.frontend`:

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY src/frontend/package.json src/frontend/package-lock.json* ./
RUN npm ci
COPY src/frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx config to proxy /api and /data to backend
RUN printf 'server {\n\
    listen 80;\n\
    location / {\n\
        root /usr/share/nginx/html;\n\
        try_files $uri /index.html;\n\
    }\n\
    location /api/ {\n\
        proxy_pass http://backend:8000;\n\
    }\n\
    location /data/ {\n\
        proxy_pass http://backend:8000;\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s \
  CMD wget -q --spider http://localhost/ || exit 1
```

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml Dockerfile.backend Dockerfile.frontend
git commit -m "feat: update Docker configs for MVP architecture"
```

---

## Task 13: Integration Test & Final Cleanup

**Files:**
- Modify: `.gitignore`
- Remove: `requirements-backend.txt` (replaced by `requirements.txt`)
- Remove: `docker/init-db.sql` (no PostgreSQL in MVP)
- Remove: `docker/nginx.conf` (nginx config is inline in Dockerfile)

- [ ] **Step 1: Clean up obsolete files**

```bash
rm -f requirements-backend.txt docker/init-db.sql docker/nginx.conf
rmdir docker/ 2>/dev/null || true
```

- [ ] **Step 2: Run full backend test suite**

```bash
python -m pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 3: Verify frontend builds**

```bash
cd src/frontend && npm run build
```

Expected: Build succeeds, output in `dist/`.

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "chore: clean up obsolete files, verify full build"
```

---

## Summary

| Task | What it builds | Tests |
|------|---------------|-------|
| 1 | Pydantic models | 4 tests |
| 2 | DataStore (pandas QTL loader) | 8 tests |
| 3 | JBrowse config generator | 5 tests |
| 4 | FastAPI app + all routers | 9 tests |
| 5 | Data pipeline scripts + Makefile | Manual (run `make data`) |
| 6 | Frontend scaffolding (React + Vite + Tailwind) | npm install + compile |
| 7 | API client + React hooks | Type-checked |
| 8 | App shell + species selector | Visual |
| 9 | QTL explorer + detail panel | Visual |
| 10 | Search bar | Visual |
| 11 | JBrowse 2 genome browser integration | Visual |
| 12 | Docker configuration | `docker compose up` |
| 13 | Integration test + cleanup | Full suite |

**Total:** 26 backend tests, frontend type-checking, visual verification.

**To run the full MVP after completing all tasks:**
```bash
make data          # Download + process genome data (~6 GB, takes a while)
make dev-backend   # Terminal 1: start FastAPI on :8000
make dev-frontend  # Terminal 2: start Vite on :3000
# Open http://localhost:3000
```
