# Saudi Livestock QTL Data Sources

---

## 1. Reference Genomes

### 1.1 Sheep (Ovis aries)

**Primary Assembly:** Oar_rambouillet_v1.0
**Source:** NCBI Assembly GCF_002742125.1
**Download:**
```bash
wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/002/742/125/GCF_002742125.1_Oar_rambouillet_v1.0/GCF_002742125.1_Oar_rambouillet_v1.0_genomic.fna.gz
wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/002/742/125/GCF_002742125.1_Oar_rambouillet_v1.0/GCF_002742125.1_Oar_rambouillet_v1.0_genomic.gff.gz
```

**Size:** ~2.7 Gb
**Format:** FASTA + GFF3 annotations
**Date:** 2020 release

### 1.2 Camel (Camelus dromedarius)

**Primary Assembly:** CamDro2
**Source:** NCBI / KAUST (if available)
**Download:**
```bash
# Check NCBI for latest camel assembly
wget https://ftp.ncbi.nlm.nih.gov/genomes/all/[camel-assembly-id]/[camel-assembly-id]_genomic.fna.gz
```

**Size:** ~2.5 Gb
**Format:** FASTA + GFF3 annotations
**Note:** Emerging field, data sources may be limited

### 1.3 Cattle (Bos taurus)

**Primary Assembly:** ARS-UCD1.2
**Source:** Ensembl Cattle
**Download:**
```bash
wget ftp://ftp.ensembl.org/pub/release-108/fasta/bos_taurus/dna/Bos_taurus.ARS-UCD1.2.dna.toplevel.fa.gz
```

**Size:** ~2.7 Gb

### 1.4 Goat (Capra hircus)

**Primary Assembly:** CHIR_1.0
**Source:** Ensembl Goat
**Download:**
```bash
wget ftp://ftp.ensembl.org/pub/release-108/fasta/capra_hircus/dna/Capra_hircus.CHIR_1.0.dna.toplevel.fa.gz
```

**Size:** ~2.7 Gb

### 1.5 Horse (Equus caballus)

**Primary Assembly:** EquCab3.0
**Source:** Ensembl Equus caballus
**Download:**
```bash
# Horse genome
wget ftp://ftp.ensembl.org/pub/release-111/fasta/equus_caballus/dna/Equus_caballus.EquCab3.0.dna.toplevel.fa.gz

# Horse gene annotations
wget ftp://ftp.ensembl.org/pub/release-111/gff3/equus_caballus/Equus_caballus.EquCab3.0.111.gff3.gz
```

**Size:** ~2.7 Gb
**Format:** FASTA + GFF3 annotations
**Alternative:** EquCab2.0 (older, more legacy data)

**Saudi Arabian Horse Breeds:**
- **Arabian (Asil)** - Purebred, cultural significance
- **Najdi** - Desert-adapted, endurance
- **Sudairy** - Racing bloodlines
- **Sowda** - Traditional breeding

---

## 2. Gene Annotations

### 2.1 Sheep Gene Annotations (Ensembl)
**URL:** https://www.ensembl.org/Ovis_aries/Info/Index
**Download:**
```bash
wget ftp://ftp.ensembl.org/pub/release-108/gff3/ovis_aries/Ovis_aries.Oar_rambouillet_v1.0.108.gff3.gz
```

### 2.2 Camel Gene Annotations
**Source:** NCBI or KAUST (if camel-specific annotations available)

### 2.3 Cattle Gene Annotations
**URL:** https://www.ensembl.org/Bos_taurus/Info/Index
**Download:**
```bash
wget ftp://ftp.ensembl.org/pub/release-108/gff3/bos_taurus/Bos_taurus.ARS-UCD1.2.108.gff3.gz
```

### 2.4 Goat Gene Annotations
**URL:** https://www.ensembl.org/Capra_hircus/Info/Index
**Download:**
```bash
wget ftp://ftp.ensembl.org/pub/release-108/gff3/capra_hircus/Capra_hircus.CHIR_1.0.108.gff3.gz
```

### 2.5 Horse Gene Annotations (Ensembl)
**URL:** https://www.ensembl.org/Equus_caballus/Info/Index
**Download:**
```bash
wget ftp://ftp.ensembl.org/pub/release-111/gff3/equus_caballus/Equus_caballus.EquCab3.0.111.gff3.gz
```

**Content:**
- Gene locations
- Transcript isoforms
- Exon/intron structure
- Protein features

---

## 3. QTL Data

### 3.1 Sheep QTL (Animal QTLdb)

**URL:** https://www.animalgenome.org/cgi-bin/QTLdb/OA/index
**Download:**
```bash
wget https://www.animalgenome.org/QTLdb/export/Ovis_aries/QTL/Ovis_aries_QTL_all.bed
wget https://www.animalgenome.org/QTLdb/export/Ovis_aries/QTL/Ovis_aries_QTL_all.xlsx
```

**Entries:** ~10,000 QTLs

### 3.2 Camel QTL

**Source:** Emerging field, limited public data
**Options:**
- Search KAUST publications for camel QTL studies
- Contact Saudi research institutions
- Monitor Animal QTLdb for camel entries

**Note:** Research opportunity - contribute camel QTL mapping to field

### 3.3 Cattle QTL (Animal QTLdb)

**URL:** https://www.animalgenome.org/cgi-bin/QTLdb/BT/index
**Download:**
```bash
wget https://www.animalgenome.org/QTLdb/export/Bos_taurus/QTL/Bos_taurus_QTL_all.bed
wget https://www.animalgenome.org/QTLdb/export/Bos_taurus/QTL/Bos_taurus_QTL_all.xlsx
```

**Entries:** ~15,000 QTLs

### 3.4 Goat QTL (Animal QTLdb)

**URL:** https://www.animalgenome.org/cgi-bin/QTLdb/CH/index
**Download:**
```bash
wget https://www.animalgenome.org/QTLdb/export/Capra_hircus/QTL/Capra_hircus_QTL_all.bed
wget https://www.animalgenome.org/QTLdb/export/Capra_hircus/QTL/Capra_hircus_QTL_all.xlsx
```

**Entries:** ~8,000 QTLs

### 3.5 Horse QTL (Animal QTLdb)

**Primary Source:** Animal QTLdb - Equine
**URL:** https://www.animalgenome.org/cgi-bin/QTLdb/EC/index
**Download:**
```bash
wget https://www.animalgenome.org/QTLdb/export/Equus_caballus/QTL/Equus_caballus_QTL_all.bed
wget https://www.animalgenome.org/QTLdb/export/Equus_caballus/QTL/Equus_caballus_QTL_all.xlsx
```

**Entries:** ~5,000 QTLs

**QTL Focus Areas (Horse):**
- Performance traits (speed, endurance)
- Conformation QTLs
- Health traits (disease resistance)
- Gait characteristics

**Total QTL Data:** ~38,000 entries across all 5 species

---

## 4. Comparative Genomics Data

### 4.1 Synteny Maps

**Source:** Ensembl Compara
**Download:**
```bash
# Sheep vs Camel (if available)
wget https://ftp.ensembl.org/pub/current-release/compara/species/Ovis_aries_vs_Camelus_dromedarius.txt

# Sheep vs Cattle
wget https://ftp.ensembl.org/pub/current-release/compara/species/Ovis_aries_vs_Bos_taurus.txt

# Sheep vs Goat
wget https://ftp.ensembl.org/pub/current-release/compara/species/Ovis_aries_vs_Capra_hircus.txt

# Sheep vs Horse
wget https://ftp.ensembl.org/pub/current-release/compara/species/Ovis_aries_vs_Equus_caballus.txt

# Plus 6 more species pairs (10 total combinations)
```

### 4.2 Ortholog Relationships

**Download:**
```bash
# Orthologs for all species
wget https://ftp.ensembl.org/pub/current-release/compara/species/Ovis_aries_orthologs.txt
wget https://ftp.ensembl.org/pub/current-release/compara/species/Bos_taurus_orthologs.txt
wget https://ftp.ensembl.org/pub/current-release/compara/species/Capra_hircus_orthologs.txt
wget https://ftp.ensembl.org/pub/current-release/compara/species/Equus_caballus_orthologs.txt
```

### 4.3 Species Combinations for Synteny

**10 Species Pairs:**
1. Sheep ↔ Camel
2. Sheep ↔ Cattle
3. Sheep ↔ Goat
4. Sheep ↔ Horse
5. Camel ↔ Cattle
6. Camel ↔ Goat
7. Camel ↔ Horse
8. Cattle ↔ Goat
9. Cattle ↔ Horse
10. Goat ↔ Horse

---

## 5. Additional Data Sources

### 5.1 Sheep HapMap Project
**URL:** https://www.sheephapmap.org/
**Content:** SNP data, breed diversity

### 5.2 Horse Breed Data (Saudi Arabia)

**Saudi Arabian Horse Breeds:**
- **World Arabian Horse Organization (WAHO):** https://www.waho.org/
- **Saudi Equestrian Federation (SEF):** Regional registry
- **King Abdulaziz Arabian Horse Center:** https://kahc.gov.sa/
- **Private Breeders:** Local Arabian horse farms

### 5.3 Literature (for QTL references)

**PubMed API:** https://www.ncbi.nlm.nih.gov/pmc/tools/oai/
**Usage:** Get full-text papers for QTL citations

### 5.4 KAUST / KACST Research

**KAUST Genome Resources:** https://www.kaust.edu.sa/research/
**KACST Agricultural Research:** https://www.kacst.edu.sa/

**Potential collaboration opportunities for:**
- Camel genomics (KAUST strength)
- Saudi breed data compilation
- Regional trait annotations

---

## 6. Data Processing Workflow

### 6.1 Download and Validate (All Species)

**For each species:**
```bash
# Download genome
wget [FASTA URL] -O [species]_genome.fa.gz
gunzip [species]_genome.fa.gz

# Download annotations
wget [GFF3 URL] -O [species]_annotations.gff3.gz
gunzip [species]_annotations.gff3.gz

# Validate
samtools faidx [species]_genome.fa
```

### 6.2 Create Indexes

```bash
# FAI index (required by JBrowse)
samtools faidx [species]_genome.fa

# Tabix index (for GFF3)
bgzip [species]_annotations.gff3
tabix -p gff [species]_annotations.gff3.gz
```

### 6.3 Convert QTL to BED

```bash
# If QTL data in Excel/CSV
python3 scripts/convert_qtl_to_bed.py --input qtl_data.xlsx --output qtl_data.bed
```

### 6.4 Load into Database

```bash
# For JBrowse
python3 scripts/jb2_prepare.py \
  --genome [species]_genome.fa \
  --gff [species]_annotations.gff3 \
  --output data/jbrowse_data/
```

---

## 7. Data Quality Checks

### 7.1 Genome Validation
- Check file integrity (MD5 checksums)
- Verify chromosome naming consistency (chr1 vs 1)
- Check for gaps/Ns in sequence
- Compare reported size vs actual size

### 7.2 Annotation Validation
- Check GFF3 format compliance
- Verify gene IDs match genome
- Check for overlapping features
- Validate coordinate ranges

### 7.3 QTL Validation
- Remove duplicates
- Check coordinate ranges
- Validate trait classifications
- Cross-reference with Animal QTLdb

### 7.4 Cross-Species Validation
- Ensure consistent coordinate systems
- Verify species IDs match across datasets
- Check synteny data completeness

---

## 8. Data Storage Requirements

### Estimated Disk Usage

| Species | Genome (FASTA) | Annotations (GFF3) | QTL Data | Total |
|----------|------------------|---------------------|-----------|--------|
| Sheep | 2.7 GB | 500 MB | 50-100 MB | ~3.2 GB |
| Camel | 2.5 GB | 500 MB | Emerging | ~3.0 GB |
| Cattle | 2.7 GB | 500 MB | 150-200 MB | ~3.4 GB |
| Goat | 2.7 GB | 500 MB | 80-100 MB | ~3.3 GB |
| **Horse** | 2.7 GB | 500 MB | 80-100 MB | ~3.3 GB |
| **TOTAL** | ~13.3 GB | ~2.5 GB | ~0.6 GB | **~16-17 GB** |

### Compression
- Use gzip for FASTA/GFF3 files
- Use tabix for indexed queries
- Use PostgreSQL for QTL data (space-efficient)

---

## 9. Update Schedule

### Regular Updates
- **Genome/Annotations:** Check Ensembl releases (every 3-4 months)
- **QTL Data:** Monitor Animal QTLdb (ongoing)
- **Comparative Data:** Update when new assemblies released
- **Horse QTL:** Monitor equine research publications

### Versioning
- Keep track of assembly versions
- Document data download dates
- Archive older versions if needed

---

## 10. Scripts and Tools

### Required Tools
```bash
# Data processing
samtools 1.15+          # Genome indexing
bedtools 2.31+          # BED file operations
bcftools 1.15+          # VCF handling (if needed)

# Python packages
pysam                    # FASTA/GFF3 parsing
pandas                    # QTL data processing
biopython                 # Sequence operations
```

### Helper Scripts (to create)
- `scripts/download_genome.py` - Automate data download for all species
- `scripts/convert_qtl_to_bed.py` - Format conversion
- `scripts/validate_gff3.py` - Quality checks
- `scripts/prepare_jbrowse.py` - JBrowse data prep
- `scripts/compile_breeds.py` - Compile Saudi breed data

---

## 11. Saudi Breed Data Compilation

### 11.1 Data Collection Sources

**Arabian Horse Breeds:**
- WAHO registry data
- Saudi Equestrian Federation
- King Abdulaziz Arabian Horse Center
- Private breeder databases

**Other Species:**
- Saudi Agricultural research papers
- Local breed surveys
- KAUST/KACST collaborations

### 11.2 Breed Data Structure

```sql
CREATE TABLE saudi_breeds (
    id INTEGER PRIMARY KEY,
    species_id INTEGER REFERENCES species(id),
    breed_name TEXT,
    arabian_name TEXT,
    region TEXT,
    population_size INTEGER,
    notes TEXT
);
```

### 11.3 Breed Traits to Capture

**Heat Tolerance:**
- Desert adaptation markers
- Water efficiency traits
- Temperature regulation QTLs

**Disease Resistance:**
- Local pathogen resistance
- Breed-specific health traits
- Genetic immunity markers

**Performance:**
- Growth rate QTLs
- Production traits
- For Arabian horses: speed, endurance

---

## 12. Species Priority for Implementation

### Phase 1 (Weeks 1-2): Priority Species
1. **Sheep** (Ovis aries) - High priority, extensive data
2. **Camel** (Camelus dromedarius) - Saudi focus, emerging field
3. **Horse** (Equus caballus) - High cultural significance

### Phase 2 (Weeks 6-8): Secondary Species
4. **Cattle** (Bos taurus) - Well-studied, good reference
5. **Goat** (Capra hircus) - Widespread in Kingdom

---

**Last Updated:** April 8, 2026
**Next Review:** After initial prototype completion

---

## 13. Collaboration Opportunities

### Saudi Institutions
- **KAUST:** Genomics research, camel expertise
- **KACST:** Agricultural research, livestock improvement
- **King Abdulaziz Arabian Horse Center:** Horse breed data
- **Saudi Universities:** Local breed knowledge

### International Resources
- **Ensembl:** All 5 species assemblies
- **NCBI:** Genome data and QTLs
- **Animal QTLdb:** All livestock QTL data
- **World Arabian Horse Organization:** Breed standards

---

*Comprehensive data sources guide for 5 Saudi livestock species*
*Added Horse species - April 8, 2026*
