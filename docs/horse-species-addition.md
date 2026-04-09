# Horse Species Addition

**Added:** April 8, 2026
**Species:** Horse (Equus caballus)

---

## 🐴 Why Include Horse?

### Saudi Context
- **Cultural Heritage:** Horses hold deep cultural significance in Saudi Arabia
- **Equestrian Sports:** Growing interest in Arabian horse racing and show events
- **Arabian Breeds:** World-renowned for beauty, endurance, and speed
- **Investment Value:** High-value breeding industry

### Scientific Relevance
- **Equine Genomics:** Well-studied field with extensive data
- **Comparative Value:** Provides evolutionary context across ungulates
- **Trait Mapping:** Performance, conformation, disease resistance QTLs
- **Breeding Programs:** Saudi Arabian horse improvement initiatives

---

## 📊 Horse Genome Data

### Assembly Options
1. **EquCab3.0** (Ensembl release 111)
   - High-quality reference assembly
   - Well-annotated
   - Download: Ensembl Equus caballus

2. **EquCab2.0** (Older but widely used)
   - Extensive legacy data
   - Good for comparative studies

### Expected Size
- **Genome:** ~2.7 Gb
- **Gene Annotations:** ~500 MB (GFF3)
- **QTL Data:** ~5,000 entries (Animal QTLdb)

---

## 🔗 Data Sources

### Primary Sources
- **Ensembl Equus caballus:** https://www.ensembl.org/Equus_caballus/Info/Index
- **NCBI Horse Genome:** https://www.ncbi.nlm.nih.gov/genome/?term=Equus+caballus
- **Animal QTLdb:** https://www.animalgenome.org/cgi-bin/QTLdb/EC/index

### Arabian Breed Resources
- **Arabian Horse Association:** Saudi/International registries
- **KAUST Equine Research:** Potential collaboration
- **Saudi Equestrian Federation:** Breed data sources

---

## 🎯 Saudi Arabian Horse Breeds

| Breed | Region | Notes |
|--------|---------|--------|
| **Arabian (Asil)** | Nationwide | Purebred, cultural significance |
| **Najdi** | Najd region | Desert-adapted, endurance |
| **Sudairy** | Northern regions | Racing bloodlines |
| **Sowda** | Eastern regions | Traditional breeding |

---

## 📅 Integration Timeline

### Updated Project Phases

**Phase 1:** Setup (Week 1-2)
- Load sheep + camel + horse (3 species now)
- Test multi-species switching

**Phase 2:** QTL Integration (Week 3-6)
- QTL data for all 5 species
- Species-specific filtering

**Phase 3:** Add Cattle + Goat (Week 7-9)
- Complete 5-species coverage

**Phase 4:** Saudi Focus (Week 10-13)
- Arabian breed annotations (including horses)
- Equestrian trait mapping
- Full deployment

---

## 🧬 Trait Focus (Horse)

### Performance Traits
- Speed QTLs (racing performance)
- Endurance markers
- Conformation QTLs
- Gait characteristics

### Health Traits
- Disease resistance (e.g., laminitis, colic)
- Metabolic efficiency
- Respiratory health markers

### Arabian Horse Focus
- **Breed preservation:** Genetic diversity mapping
- **Conformation traits:** Traditional breed standards
- **Performance:** Racing and show qualities
- **Regional adaptation:** Desert climate traits

---

## 🔧 Technical Updates

### JBrowse 2 Configuration
Add horse as 5th species:
```javascript
assemblies: {
  'Oar_rambouillet_v1.0': { name: 'Sheep', ... },
  'CamDro2': { name: 'Camel', ... },
  'ARS-UCD1.2': { name: 'Cattle', ... },
  'CHIR_1.0': { name: 'Goat', ... },
  'EquCab3.0': { name: 'Horse', ... }
}
```

### Database Schema Update
Add horse to species table:
```sql
INSERT INTO species (name, scientific_name, assembly)
VALUES ('Horse', 'Equus caballus', 'EquCab3.0');
```

---

## 📊 Updated Data Requirements

### Final Species Count: 5

| Species | Assembly | Size | Status |
|----------|-----------|-------|--------|
| Sheep | Oar_rambouillet_v1.0 | 2.7 Gb | Ready |
| Camel | CamDro2 | 2.5 Gb | Emerging |
| Cattle | ARS-UCD1.2 | 2.7 Gb | Ready |
| Goat | CHIR_1.0 | 2.7 Gb | Ready |
| Horse | EquCab3.0 | 2.7 Gb | Ready |

**Total Storage:** ~14-16 GB (all 5 species)

---

## 🎯 Success Metrics (Updated)

### Scientific Impact
- [ ] Enables comprehensive Saudi livestock genomics
- [ ] Supports Arabian horse breeding programs
- [ ] Facilitates equine trait research
- [ ] Cross-species insights (5 ungulates)
- [ ] Platform for Saudi equestrian community

---

## 💰 Cost Impact

**Additional Storage:** ~2-3 Gb (horse genome + annotations)
**Development Time:** +1-2 weeks (horse QTL integration)
**Financial Cost:** $0 (still uses existing resources)

---

## 📞 Next Actions

### Immediate
1. ✅ Added horse to documentation
2. [ ] Update JBrowse 2 config for 5 species
3. [ ] Download EquCab3.0 genome
4. [ ] Research Arabian horse breed data

### This Week
1. [ ] Integrate horse into architecture docs
2. [ ] Update data sources with horse links
3. [ ] Plan Arabian horse trait annotations

---

## 🌐 Collaboration Opportunities (Horse)

### Saudi Partners
- **Saudi Equestrian Federation** (SEF)
- **King Abdulaziz Arabian Horse Center**
- **Private breeders** (Arabian horse farms)

### International Resources
- **World Arabian Horse Organization (WAHO)** (if relevant)
- **International equine QTL databases**

---

## 🚀 Why This Matters

**Cultural + Scientific:**
- Honors Saudi heritage (Arabian horses)
- Adds valuable comparative genomics data
- Supports growing equestrian industry
- Enables breed preservation and improvement

**Research Value:**
- **5th ungulate species** enhances comparative power
- **Well-studied equine genomics** provides good reference
- **Performance trait mapping** applicable to other species
- **Equestrian sports** growing in Saudi Arabia

---

**Project Status:** Now 5 Saudi livestock species
**Species:** Sheep, Camel, Cattle, Goat, Horse
**Updated:** April 8, 2026

---

*Horse added to expand Saudi livestock coverage*
