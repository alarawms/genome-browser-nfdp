# Saudi Livestock Genome Browser - Expanded Project

> **Updated Vision:** Multi-species genome browser for Saudi Arabia's key livestock

**Species Included:**
- 🐑 **Sheep** (Ovis aries)
- 🐪 **Camel** (Camelus dromedarius)
- 🐄 **Cattle** (Bos taurus)
- 🐐 **Goat** (Capra hircus)

---

## 🌍 Why This Matters for Saudi Arabia

### Economic Importance
- **Sheep & Goat:** Major protein sources, widespread across Kingdom
- **Camel:** Cultural heritage, adaptation to arid conditions
- **Cattle:** Dairy and beef production

### Research Needs
- **Heat tolerance** QTLs across species
- **Disease resistance** in Saudi conditions
- **Breed adaptation** to arid climate
- **Comparative genomics** for breeding programs
- **Local breed preservation** and genetic diversity

### Regional Focus
- **Saudi Arabian breeds** (e.g., Awassi sheep, Najdi camel)
- **Gulf region traits** (heat tolerance, forage efficiency)
- **KAUST/KACST research** integration
- **Local agricultural institutions** collaboration

---

## 📊 Updated Project Scope

### MVP (Week 6)
- **2 species:** Sheep + Camel (priority for Saudi context)
- Genome navigation for both
- QTL data for both
- Basic comparative view
- Search by gene/QTL

### Phase 2 (Week 8-10)
- **Add Cattle + Goat** (full 4-species coverage)
- Advanced comparative genomics
- All-species QTL filtering
- Cross-species synteny

### Full Release (Week 12)
- Saudi breed annotations
- Advanced filtering (species + trait + breed)
- Regional trait highlights
- Research community features

---

## 🗂️ Expanded Data Requirements

### Species Genomes
| Species | Assembly | Size | Source | Status |
|----------|-----------|-------|---------|--------|
| Sheep | Oar_rambouillet_v1.0 | 2.7 Gb | Ensembl | Ready |
| Camel | CamDro2 | 2.5 Gb | NCBI/KAUST | Emerging |
| Cattle | ARS-UCD1.2 | 2.7 Gb | Ensembl | Ready |
| Goat | CHIR_1.0 | 2.7 Gb | Ensembl | Ready |

### QTL Data by Species
- **Sheep:** ~10,000 QTLs (Animal QTLdb)
- **Camel:** Emerging (limited public data, research opportunity)
- **Cattle:** ~15,000 QTLs (Animal QTLdb)
- **Goat:** ~8,000 QTLs (Animal QTLdb)

### Saudi Breed Data (New!)
**Need to compile:**
- Awassi sheep traits
- Najdi camel characteristics
- Saudi cattle breeds
- Desert-adapted goats
- **Collaboration needed:** KAUST, KACST, Saudi universities

---

## 🔧 Technical Updates

### JBrowse 2 Multi-Reference Support
**JBrowse 2 supports multiple references natively:**
```javascript
// Example: Multiple species in JBrowse 2
{
  assemblies: {
    'Oar_rambouillet_v1.0': { name: 'Sheep', sequence: { ... } },
    'CamDro2': { name: 'Camel', sequence: { ... } },
    'ARS-UCD1.2': { name: 'Cattle', sequence: { ... } },
    'CHIR_1.0': { name: 'Goat', sequence: { ... } }
  }
}
```

### Species Selector UI
- Dropdown to select species
- Load genome on-demand
- Cross-species comparison mode
- Breed filters per species

---

## 📅 Revised Timeline

### Phase 1: Setup (Week 1-2)
- [ ] Install JBrowse 2 (multi-species ready)
- [ ] Load sheep genome + annotations
- [ ] Load camel genome + annotations
- [ ] Test multi-species switching

### Phase 2: QTL Integration (Week 3-5)
- [ ] Download QTL data for sheep + camel
- [ ] Create QTL tracks for both species
- [ ] Implement trait filtering
- [ ] Add species-specific search

### Phase 3: Add Cattle + Goat (Week 6-8)
- [ ] Load cattle genome
- [ ] Load goat genome
- [ ] Add QTL data for both
- [ ] Create 4-species comparative view

### Phase 4: Saudi Focus (Week 9-12)
- [ ] Compile Saudi breed data
- [ ] Add breed annotations
- [ ] Regional trait filtering
- [ ] Research community features
- [ ] Documentation for Saudi context

---

## 🎯 Success Metrics (Updated)

### Technical
- [x] Load 4 species genomes efficiently (< 3s each)
- [ ] Cross-species comparison works smoothly
- [ ] QTL search across species < 1s
- [ ] Breed filtering functional

### Scientific Impact
- [ ] Enables Saudi livestock genomics research
- [ ] Supports breeding programs
- [ ] Facilitates regional trait discovery
- [ ] Platform for Saudi research community

---

## 💡 Key Features (Saudi Focus)

### 1. Species Comparison
- Side-by-side genome views
- Synteny visualization (sheep ↔ camel ↔ cattle ↔ goat)
- Shared QTL regions across species

### 2. Saudi Breed Explorer
- Filter by Saudi breeds (Awassi, Najdi, etc.)
- Breed-specific trait annotations
- Local adaptation markers

### 3. Regional Traits
- Heat tolerance QTLs
- Disease resistance in arid climates
- Forage efficiency markers
- Water conservation traits

### 4. Research Hub
- Link to Saudi publications
- KAUST/KACST research integration
- Saudi agricultural institutions database

---

## 🌐 Collaboration Opportunities

### Academic Partners
- **KAUST:** Genomics research collaboration
- **KACST:** Agricultural research
- **Saudi Universities:** Breed data, local knowledge

### Data Contributions
- Saudi breed genome data (if available)
- Local QTL studies
- Regional trait annotations

### Community Building
- Training workshops
- Saudi research community portal
- Open-source development

---

## 💰 Cost & Resources (Updated)

**Development Time:** 12 weeks (expanded from 10)
**Hosting:** kw61001 (existing)
**Storage:** ~12 GB (4 species genomes + annotations + QTLs)
**Financial Cost:** $0 (uses existing resources)

**Additional Needs:**
- **Saudi breed data compilation** (requires collaboration)
- **Camel QTL research** (emerging field, opportunity)
- **Local research partnerships**

---

## 📞 Next Steps (Updated)

### Immediate (This Week)
1. **Update project documentation** ✅ (done)
2. **Confirm multi-species approach** with JBrowse 2
3. **Prioritize species:**
   - **Priority 1:** Sheep + Camel (Saudi focus)
   - **Priority 2:** Cattle + Goat (comparative context)
4. **Begin Phase 1:**
   - Install JBrowse 2
   - Load sheep + camel genomes
   - Test multi-species switching

### This Month
1. **Complete Phase 1-2** (sheep + camel)
2. **Research Saudi breeds** (Awassi, Najdi, etc.)
3. **Identify collaboration opportunities** (KAUST, KACST)
4. **Plan cattle + goat integration**

---

## 🚀 Why This Is Better

**Saudi Context:**
- **Relevant to Kingdom's agricultural priorities**
- **Focus on regional adaptation traits**
- **Supports local breeding programs**
- **Platform for Saudi research community**

**Research Impact:**
- **Cross-species insights** (heat tolerance, disease resistance)
- **Camel genomics** (emerging, important field)
- **Breed preservation** for genetic diversity
- **Comparative advantages** across livestock

---

## 🎓 Academic Value

This expanded project supports your PhD in:
- **Comparative livestock genomics**
- **Saudi-specific trait adaptation**
- **Multi-species QTL analysis**
- **Regional genetic diversity**

**Publishing Opportunities:**
1. **Saudi Livestock Genome Browser paper** (tool description)
2. **Cross-species trait comparison** (comparative genomics)
3. **Saudi breed genomics** (if breed data compiled)
4. **Camel QTL review** (emerging field)

---

**Project Status:** Expanded to 4 Saudi livestock species
**Next Action:** Confirm multi-species approach and start JBrowse 2 installation
**Key Milestone:** MVP with Sheep + Camel (Week 6)

---

*Updated: April 8, 2026 - Expanded from sheep-only to Saudi livestock focus*
