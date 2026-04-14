DATA_DIR ?= data

.PHONY: data data-docker process-docker download-genomes download-annotations download-qtls \
        index-genomes convert-qtls prepare-tracks enrich-ontologies \
        setup add-genome register-annotation build-custom-animal \
        dev-backend dev-frontend dev test clean

## === Setup ===

setup:
	@echo "Setting up environment..."
	@if command -v conda >/dev/null 2>&1; then \
		echo "  conda found — creating environment from environment.yml"; \
		conda env create -f environment.yml || conda env update -f environment.yml; \
		echo "  ✓ Run: conda activate genome-browser"; \
	else \
		echo "  No conda found. Options:"; \
		echo "    1. Install conda: https://docs.conda.io/en/latest/miniconda.html"; \
		echo "    2. Use Docker:  make data-docker"; \
	fi

## === Data Pipeline ===

data: download-genomes download-annotations download-qtls index-genomes convert-qtls prepare-tracks
	@echo ""
	@echo "✓ Genomes and annotations ready."
	@echo "  If QTL data was missing, the browser still works (no QTL track)."
	@echo "  See above for manual QTL download instructions."

data-docker:
	docker build -t genome-browser-data -f Dockerfile.data-pipeline .
	docker run --rm --user $(shell id -u):$(shell id -g) -v $(CURDIR)/$(DATA_DIR):/data genome-browser-data

process-docker:
	docker build -t genome-browser-data -f Dockerfile.data-pipeline .
	docker run --rm --user $(shell id -u):$(shell id -g) --entrypoint make -v $(CURDIR)/$(DATA_DIR):/data genome-browser-data \
		index-genomes convert-qtls prepare-tracks DATA_DIR=/data

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

## Enrich every qtls.json under $(DATA_DIR)/qtl/ with ontology term IDs.
## Requires network (EBI OLS); BIOPORTAL_API_KEY env enables LPT lookups too.
enrich-ontologies:
	@for f in $(DATA_DIR)/qtl/*/qtls.json; do \
		[ -f "$$f" ] && python3 scripts/enrich_qtl_ontologies.py "$$f"; \
	done

## === Add Custom Genome ===

add-genome:
ifndef FASTA
	@echo "Usage: make add-genome FASTA=/path/to/assembly.fa ID=species_id [NAME=DisplayName] [ASSEMBLY=AssemblyName] [SCIENTIFIC='Scientific name']"
	@exit 1
endif
ifndef ID
	@echo "Error: ID is required. Example: make add-genome FASTA=my.fa ID=camel"
	@exit 1
endif
	bash scripts/add_genome.sh "$(ID)" "$(FASTA)" "$(or $(ASSEMBLY),$(ID))" "$(or $(NAME),$(ID))" "$(or $(SCIENTIFIC),)"

## Register a new gene-annotation GFF as a track for an existing species.
## Usage:
##   make register-annotation ID=najdi SLUG=braker3 LABEL="Genes (BRAKER3)" GFF=/path/to/a.gff3 [PRIMARY=1]
register-annotation:
ifndef ID
	@echo "Error: ID is required (species_id, e.g. najdi)"; @exit 1
endif
ifndef SLUG
	@echo "Error: SLUG is required (short track id, e.g. braker3)"; @exit 1
endif
ifndef LABEL
	@echo "Error: LABEL is required (e.g. \"Genes (BRAKER3 de novo)\")"; @exit 1
endif
ifndef GFF
	@echo "Error: GFF is required (path to the annotation GFF3)"; @exit 1
endif
	bash scripts/register_annotation.sh "$(ID)" "$(SLUG)" "$(LABEL)" "$(GFF)" $(if $(PRIMARY),--primary,)

## Full per-animal track build: lift QTLs from DONOR, index GFF, compute QTL-gene
## overlap, run ontology enrichment. Requires paftools.js + bgzip + tabix on PATH.
##
## Usage:
##   make build-custom-animal ID=najdi DONOR=sheep PAF=/path/alignment.paf GFF=/path/liftoff.gff3
build-custom-animal:
ifndef ID
	@echo "Error: ID is required"; @exit 1
endif
ifndef DONOR
	@echo "Error: DONOR is required (species to lift QTLs from, e.g. sheep)"; @exit 1
endif
ifndef PAF
	@echo "Error: PAF is required (minimap2 alignment, query=donor target=this animal)"; @exit 1
endif
ifndef GFF
	@echo "Error: GFF is required (liftoff-produced gene annotation in target coords)"; @exit 1
endif
	bash scripts/build_custom_animal_tracks.sh "$(ID)" "$(DONOR)" "$(PAF)" "$(GFF)"

## === Development ===

dev-backend:
	DATA_DIR=$(DATA_DIR) .venv/bin/python -m uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8880

dev-frontend:
	cd src/frontend && npm install && npm run dev -- --host 0.0.0.0

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
