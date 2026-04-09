# Saudi Arabia Livestock Genome Browser

> Web interface for Saudi livestock genome visualization and comparative genomics

**Created:** April 8, 2026
**Goal:** Build a web interface to display genome features for Saudi Arabia's key livestock species and enable comparative analysis

---

## 🎯 Project Vision

Create a web-based genome browser and visualization platform for Saudi Arabia's livestock:
- **Primary species:** Sheep, Camel, Cattle, Goat, Horse
- QTL (Quantitative Trait Loci) data
- Comparative genomics across species
- Feature annotation and exploration
- **Regional focus:** Saudi Arabian breeds and traits

---

## 🧬 Core Features

### 1. Genome Browser Interface
- Interactive chromosome visualization
- Zoomable genome tracks
- Gene/QTL markers
- Search functionality

### 2. QTL Data Display
- Trait annotations
- Statistical associations
- Visual markers on genome
- Filtering by trait category

### 3. Comparative Genomics
- Multiple genome support (sheep, camel, cattle, goat)
- Synteny visualization across species
- Cross-species feature mapping
- Phylogenetic context for Arabian livestock
- **Saudi-specific breed comparisons**

### 4. Data Exploration
- Feature search
- Filter by region, trait, category
- Export data (CSV, JSON, BED)
- Interactive plots

---

## 🛠️ Technology Stack Options

### Option A: JBrowse 2 (Recommended)
**Pros:**
- Industry-standard genome browser
- Supports multiple reference genomes
- Built-in comparative genomics tools
- Extensive documentation
- Active community

**Components:**
- JBrowse 2 (JavaScript)
- Data adapters (BED, GFF3, VCF)
- REST API backend
- Track management

### Option B: IGV.js (Integrative Genomics Viewer)
**Pros:**
- Lightweight, fast
- Real-time visualization
- Mobile-friendly
- Good for single genome focus

**Cons:**
- Limited comparative genomics features
- Less extensible for custom workflows

### Option C: Custom React + D3.js Visualization
**Pros:**
- Full control over UI/UX
- Custom interactive features
- Tailored to QTL-specific use cases

**Cons:**
- High development effort
- Need to implement genome navigation from scratch
- Maintenance burden

---

## 📊 Data Requirements

### 1. Reference Genomes
- **Sheep (Ovis aries):** Oar_rambouillet_v1.0
- **Camel (Camelus dromedarius):** CamDro1, CamDro2, or latest
- **Cattle (Bos taurus):** ARS-UCD1.2
- **Goat (Capra hircus):** CHIR_1.0 or latest
- Chromosome sizes and structure for all species
- Gene annotations (GFF3/GTF) for all species

### 2. QTL Data
- QTL locations (BED format) for all species
- Trait associations relevant to Saudi conditions
- Statistical scores and confidence intervals
- Reference to public databases (Animal QTLdb)
- **Camel-specific data** (emerging field)

### 3. Comparative Data
- All four Saudi livestock species genomes
- Synteny maps across species
- Ortholog tables
- **Shared trait mappings** (e.g., heat tolerance, disease resistance)

### 4. Metadata
- Source, version, assembly info
- Trait classifications
- Literature references

---

## 🗂️ Project Structure

```
sheep-qtl/
├── README.md                 # This file
├── docs/
│   ├── architecture.md       # System design
│   ├── data-sources.md      # Where to get data
│   └── user-guide.md       # How to use the browser
├── data/
│   ├── genome/              # FASTA files
│   ├── annotations/          # GFF3 files
│   ├── qtl/                # QTL data (BED)
│   └── comparative/         # Cross-species data
├── src/
│   ├── backend/             # Data APIs
│   ├── frontend/            # Web UI
│   └── data-processing/     # Scripts for data prep
├── config/
│   ├── genome-browser.yaml    # JBrowse config
│   └── tracks.yaml         # Track definitions
└── tests/
    └── data-validation/     # Test data quality
```

---

## 🚀 Implementation Plan

### Phase 1: Data Collection (Week 1-2)
- [ ] Obtain sheep reference genome (Oar_rambouillet_v1.0 or similar)
- [ ] Download gene annotations from Ensembl/NCBI
- [ ] Compile QTL data from Animal QTLdb
- [ ] Prepare BED files for QTL locations
- [ ] Validate data integrity

### Phase 2: Basic Browser Setup (Week 3-4)
- [ ] Deploy JBrowse 2 instance
- [ ] Load reference genome
- [ ] Create gene annotation track
- [ ] Test basic navigation and zoom
- [ ] Add search functionality

### Phase 3: QTL Integration (Week 5-6)
- [ ] Create QTL track
- [ ] Add trait filtering
- [ ] Implement popup info boxes
- [ ] Add statistical score visualization
- [ ] Link to Animal QTLdb

### Phase 4: Comparative Genomics (Week 7-8)
- [ ] Add cattle genome as secondary track
- [ ] Implement synteny visualization
- [ ] Cross-species feature highlighting
- [ ] Phylogenetic tree display

### Phase 5: UI/UX Polish (Week 9-10)
- [ ] Custom theming
- [ ] Responsive design
- [ ] User feedback mechanism
- [ ] Documentation and tutorials

---

## 🎯 MVP Definition

**Minimum Viable Product (Week 6):**
- Two species views (sheep + camel)
- Gene tracks visible for both
- Basic QTL overlay for both
- Search by gene name/QTL ID
- Export current view as PNG

**Full Release (Week 12):**
- Four Saudi livestock species (sheep, camel, cattle, goat)
- Advanced filtering by trait and species
- Interactive comparative tools
- Full documentation
- **Saudi breed annotations**

---

## 🔗 Useful Resources

- **Animal QTLdb:** https://www.animalgenome.org/QTLdb/
- **Camel Genome Resources:** https://www.ncbi.nlm.nih.gov/genome/?term=Camelus+dromedarius
- **Ensembl Species:** 
  - Sheep: https://www.ensembl.org/Ovis_aries/
  - Camel: https://www.ensembl.org/Camelus_dromedarius/ (if available)
  - Cattle: https://www.ensembl.org/Bos_taurus/
  - Goat: https://www.ensembl.org/Capra_hircus/
- **JBrowse 2 Documentation:** https://jbrowse.org/jb2/
- **NCBI Genome Data:** https://www.ncbi.nlm.nih.gov/genome/
- **KAUST Genome Resources:** https://www.kaust.edu.sa/research/
- **Saudi Agricultural Research:** Relevant local institutions

---

## 📝 Next Steps

1. **Confirm technology stack** (JBrowse 2 recommended)
2. **Identify data sources** for all four Saudi livestock species
3. **Prioritize species** (sheep + camel first, then cattle + goat)
4. **Set up development environment**
5. **Begin data collection and preprocessing**

---

**Status:** Planning phase (expanded to Saudi livestock)
**Next action:** Get user approval on technology stack and prioritize species for data collection

---

*Project created by Sanad for SOS — April 8, 2026*
*Updated to include Saudi livestock focus — April 8, 2026*
