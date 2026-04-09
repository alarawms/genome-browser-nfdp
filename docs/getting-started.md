# 🚀 Getting Started: Sheep QTL Browser

> Quick start guide to build your genome browser

---

## 📋 Prerequisites

### Required Tools
```bash
# Node.js (v16+)
node --version

# Python 3.9+
python3 --version

# PostgreSQL (or SQLite for dev)
psql --version

# Git
git --version

# Genome tools
samtools --version
bedtools --version
```

### Install Genome Tools
```bash
# On Ubuntu/Debian
sudo apt-get install samtools bedtools

# On Mac
brew install samtools bedtools

# Verify installation
samtools faidx --help
bedtools intersect --help
```

---

## 🗂️ Project Setup

### 1. Clone/Create Project
```bash
# Navigate to ai-workspace
cd /home/sanad/ai-workspace/

# Project already created in sheep-qtl/
cd sheep-qtl/

# Initialize git
git init
```

### 2. Install JBrowse 2
```bash
# Create JBrowse 2 project
npx @jbrowse/create sheep-qtl-browser

# Navigate to project
cd sheep-qtl-browser/

# Install dependencies
npm install
```

### 3. Set Up Backend
```bash
# Create backend directory
mkdir -p src/backend

# Initialize Python environment
cd src/backend
python3 -m venv venv
source venv/bin/activate

# Install FastAPI
pip install fastapi uvicorn pydantic psycopg2-binary

# Install genome tools
pip install pysam pyfaidx pandas biopython
```

---

## 📥 Data Download

### Download Genome & Annotations
```bash
# Create data directory
mkdir -p ../data/genome ../data/annotations

# Download sheep genome (Oar_rambouillet_v1.0)
cd ../data/genome
wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/002/742/125/GCF_002742125.1_Oar_rambouillet_v1.0/GCF_002742125.1_Oar_rambouillet_v1.0_genomic.fna.gz
gunzip GCF_002742125.1_Oar_rambouillet_v1.0_genomic.fna.gz
mv GCF_002742125.1_Oar_rambouillet_v1.0_genomic.fna sheep_genome.fa

# Download gene annotations
cd ../annotations
wget ftp://ftp.ensembl.org/pub/release-108/gff3/ovis_aries/Ovis_aries.Oar_rambouillet_v1.0.108.gff3.gz
gunzip Ovis_aries.Oar_rambouillet_v1.0.108.gff3.gz
mv Ovis_aries.Oar_rambouillet_v1.0.108.gff3 sheep_annotations.gff3
```

### Download QTL Data
```bash
# Create QTL directory
mkdir -p ../data/qtl
cd ../data/qtl

# Download from Animal QTLdb
wget https://www.animalgenome.org/QTLdb/export/Ovis_aries/QTL/Ovis_aries_QTL_all.bed
wget https://www.animalgenome.org/QTLdb/export/Ovis_aries/QTL/Ovis_aries_QTL_all.xlsx

# Convert to proper BED format (if needed)
# (Will create conversion script)
```

---

## 🔧 Data Processing

### 1. Index Genome
```bash
# Navigate to data directory
cd data/genome

# Create FAI index (required by JBrowse)
samtools faidx sheep_genome.fa

# Verify index
ls sheep_genome.fa.fai  # Should exist
```

### 2. Prepare JBrowse Data
```bash
# Go back to JBrowse project root
cd ../sheep-qtl-browser/

# Add genome assembly
jbrowse add-assembly ../data/genome/sheep_genome.fa

# Add gene annotations
jbrowse add-track ../data/annotations/sheep_annotations.gff3

# Add QTL track
jbrowse add-track ../data/qtl/Ovis_aries_QTL_all.bed \
  --name "Sheep QTLs" \
  --type "FeatureTrack" \
  --adapterType "BedAdapter"
```

### 3. Start JBrowse Server
```bash
# In sheep-qtl-browser/
npm start

# Browser will open at:
# http://localhost:3000
```

---

## 🎯 Test the Browser

### 1. Navigate Genome
- Open browser
- Scroll through chromosomes
- Zoom in/out
- Find genes

### 2. Check Tracks
- Gene annotations visible?
- QTL markers showing?
- Popups working?

### 3. Search
- Search for gene name (e.g., "DGAT1")
- Search for QTL ID
- Verify results

---

## 🐍 Backend API (Basic)

### Create FastAPI App
```python
# src/backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Sheep QTL API"}

@app.get("/api/qtls")
def get_qtls():
    # Return QTL data (will implement)
    return {"qtls": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Run Backend
```bash
cd src/backend
python main.py

# API will be at:
# http://localhost:8000
```

---

## 📝 Next Steps

After basic setup:

1. **Week 1 Tasks:**
   - ✅ Load genome and annotations
   - ✅ Verify genome navigation
   - ⬜ Improve QTL track appearance
   - ⬜ Add trait filtering

2. **Week 2 Tasks:**
   - ⬜ Implement QTL search API
   - ⬜ Create filtering UI
   - ⬜ Add popup info boxes
   - ⬜ Test with real QTL data

3. **Week 3 Tasks:**
   - ⬜ Add cattle genome
   - ⬜ Create comparative view
   - ⬜ Implement synteny visualization

---

## 🐛 Troubleshooting

### Issue: Genome not loading
**Solution:**
```bash
# Check FAI index exists
ls data/genome/sheep_genome.fa.fai

# If missing, recreate:
samtools faidx data/genome/sheep_genome.fa
```

### Issue: Annotations not showing
**Solution:**
```bash
# Check GFF3 format
head -20 data/annotations/sheep_annotations.gff3

# Should start with:
##gff-version 3
```

### Issue: Port already in use
**Solution:**
```bash
# Change JBrowse port
npm run dev -- --port 3001

# Or kill existing process
lsof -ti:3000 | xargs kill -9
```

---

## 📚 Resources

- **JBrowse 2 Docs:** https://jbrowse.org/jb2/docs/
- **Genome Tools:** https://www.htslib.org/
- **Animal QTLdb:** https://www.animalgenome.org/QTLdb/

---

## 💡 Tips

1. **Start small** - Load genome first, test, then add tracks
2. **Use sample data** - Test with small region first
3. **Check console** - Browser dev tools for errors
4. **Save often** - Commit after each milestone
5. **Ask for help** - JBrowse community is active

---

**Ready to start?** Follow the steps above and your browser will be running!

*Created: April 8, 2026*
