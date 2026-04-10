DATA_DIR ?= data

.PHONY: data data-docker process-docker download-genomes download-annotations download-qtls \
        index-genomes convert-qtls prepare-tracks \
        setup add-genome dev-backend dev-frontend dev clean

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
	docker run --rm --user $(shell id -u):$(shell id -g) -v $(CURDIR)/$(DATA_DIR):/data genome-browser-data \
		make index-genomes convert-qtls prepare-tracks DATA_DIR=/data

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
