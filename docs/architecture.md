# Saudi Livestock Genome Browser Architecture

## System Design Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   User Interface                       │
│  (React.js + JBrowse 2 + Material UI or Tailwind)     │
│  - Multi-species selector (Sheep, Camel, Cattle, Goat, Horse) │
│  - Saudi breed filters                               │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              API Layer (FastAPI)                       │
│  - Multi-species genome data endpoints                 │
│  - QTL search and filtering (by species/trait)        │
│  - Comparative genomics queries across species           │
│  - Saudi breed annotations                          │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┼─────────────────┐
        │           │                 │
        ▼           ▼                 ▼
┌─────────────┐ ┌─────────────┐ ┌───────────────────┐
│  Genome     │ │    QTL      │ │  Breed & Trait   │
│  Database   │ │  Database   │ │    Database      │
│ (5 Species, │ │ (Postgres)  │ │  (Saudi Arabia) │
│  Indexed)   │ │             │ │                 │
└─────────────┘ └─────────────┘ └───────────────────┘
```

## Components

### 1. Frontend (React + JBrowse 2)
**Responsibilities:**
- Species selector (Sheep, Camel, Cattle, Goat)
- Genome navigation (zoom, pan, scroll)
- Track visualization for selected species
- Multi-species comparative view
- Search interface (gene, QTL, breed)
- Saudi breed filtering
- Export functionality

**Key Libraries:**
- `@jbrowse/react-linear-genome-view` - Genome visualization
- `@jbrowse/react-linear-comparative-view` - Cross-species comparison
- `d3-scale` - Genome coordinate scaling
- `material-ui` or `tailwindcss` - UI components
- `axios` - API communication

### 2. Backend API (FastAPI/Python)
**Responsibilities:**
- Serve genome data efficiently
- QTL search and filtering
- Comparative genomics queries
- Data preprocessing

**Endpoints:**
```
GET  /api/species                          # Available species list (5 total)
GET  /api/genome/assembly/:species     # Genome metadata by species
GET  /api/genome/region/:species/:chr/:start/:end  # Genome region
GET  /api/genes/search/:species/:query     # Gene search by species
GET  /api/qtl/list                       # All QTLs (paginated)
GET  /api/qtl/filter?species=X&trait=Y   # Filtered QTLs
GET  /api/qtl/:id                         # Single QTL details
GET  /api/breeds/:species                 # Saudi breeds by species
GET  /api/comparative/:species1/:species2    # Cross-species data
GET  /api/synteny/:species1/:species2      # Synteny blocks
POST /api/export                             # Export current view
```

### 3. Data Layer

#### Genome Database (Multi-Species Indexed FASTA + GFF3)
- **Species:**
  - Sheep (Ovis aries): Oar_rambouillet_v1.0 (~2.7 Gb)
  - Camel (Camelus dromedarius): CamDro2 (~2.5 Gb)
  - Cattle (Bos taurus): ARS-UCD1.2 (~2.7 Gb)
  - Goat (Capra hircus): CHIR_1.0 (~2.7 Gb)
  - **Horse (Equus caballus): EquCab3.0 (~2.7 Gb)**
- **Format:** Compressed FASTA (.fa.gz)
- **Index:** SAMtools FAI (.fai) per species
- **Access:** Pysam or pyfaidx for fast region extraction
- **Storage:** ~15-17 GB total

#### QTL Database (PostgreSQL)
- **Schema:**
```sql
CREATE TABLE species (
    id INTEGER PRIMARY KEY,
    name TEXT,
    scientific_name TEXT,
    assembly TEXT
);

CREATE TABLE qtls (
    id INTEGER PRIMARY KEY,
    species_id INTEGER REFERENCES species(id),
    chromosome TEXT,
    start_pos INTEGER,
    end_pos INTEGER,
    trait TEXT,
    confidence REAL,
    reference TEXT,
    pmid INTEGER
);

CREATE TABLE traits (
    id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    saudi_relevance BOOLEAN DEFAULT TRUE,
    description TEXT
);

CREATE TABLE saudi_breeds (
    id INTEGER PRIMARY KEY,
    species_id INTEGER REFERENCES species(id),
    breed_name TEXT,
    region TEXT,
    notes TEXT
);
```

#### Comparative Database (PostgreSQL)
- Synteny maps between species pairs
- Ortholog relationships (sheep ↔ camel ↔ cattle ↔ goat)
- Cross-species alignments
- Phylogenetic trees for Saudi livestock
- **Shared trait annotations** (heat tolerance, disease resistance)

### 4. Genome Browser Engine (JBrowse 2)
**Configuration:**
- Assembly YAML file (genome structure)
- Track configurations
- Data adapters (BED, GFF3, VCF)
- Rendering plugins

**Tracks (Per Species):**
1. Reference genome sequence
2. Gene annotations (GFF3)
3. QTL markers (BED)
4. Saudi breed annotations (BED/GFF3)
5. Custom tracks (user uploads)

**Comparative Tracks:**
1. Synteny blocks between species
2. Ortholog gene mappings
3. Shared trait regions
- **10 species-pair combinations** (5 species = 10 pairs)

## Deployment Options

### Option A: Local Development
- Frontend: `npm run dev` (port 3000)
- Backend: `uvicorn main:app` (port 8000)
- Data: Local filesystem (~10 GB)
- Access: http://localhost:3000

### Option B: Production Deployment
**On kw61001 (Tailscale):**
- Frontend: Nginx static serving (port 8080)
- Backend: FastAPI (port 8001)
- Data: NAS-mounted volumes (ai-workspace/livestock-genome-browser)
- Access: http://kw61001:8080/saudi-livestock-browser

- **Tailscale-only access** (private, Saudi research community)

**On Cloud (optional for broader access):**
- Frontend: Vercel/Netlify
- Backend: Railway/Render
- Data: Cloud storage (S3/B2)

## Performance Considerations

### 1. Multi-Species Genome Navigation
- **Challenge:** Loading 4 large genomes efficiently
- **Solution:**
  - Load species on-demand (not all at once)
  - Lazy loading (only visible region)
  - Data binning (downsample for zoom-out)
  - Client-side caching per species
  - Server-side compression

### 2. Cross-Species QTL Search
- **Challenge:** Searching QTLs across 5 species
- **Solution:**
  - Database indexing (species, chr, start, trait)
  - Species-specific pagination (load 100 at a time)
  - Multi-filter search (species + trait + breed)
  - Debounce search input

### 3. Comparative Genomics (5 Species)
- **Challenge:** Cross-species alignment visualization (10 species pairs)
- **Solution:**
  - Precomputed synteny blocks (10 pairs: sheep-camel, sheep-cattle, sheep-goat, sheep-horse, camel-cattle, camel-goat, camel-horse, cattle-goat, cattle-horse, goat-horse)
  - LOD score visualization
  - Progressive loading
  - Species selector to reduce initial load
  - **Arabian horse breed comparisons**

## Security Considerations

- **API rate limiting** (prevent abuse)
- **CORS configuration** (if cross-domain)
- **Input validation** (prevent injection)
- **Data sanitization** (user uploads)
- **Access logs** (track usage)

## Scalability

**Current Scope:**
- 5 Saudi livestock species (~15-17 Gb total)
- ~35,000 QTL entries across all species
- 5-species comparative genomics (10 species pairs)
- Saudi breed annotations (including Arabian horses)

**Future Expansion:**
- More Arabian breeds per species
- Additional species (e.g., poultry, other livestock)
- User accounts and custom tracks
- Shared workspaces
- **Arabian horse performance data**
- API for Saudi research community

---

**Architecture Version:** 3.0 (Multi-Species with Horse)
**Last Updated:** April 8, 2026
**Changes:** Expanded from 4 species to 5 Saudi livestock species (added horse)
