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
