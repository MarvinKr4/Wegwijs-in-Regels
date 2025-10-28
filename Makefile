SHELL=/bin/bash

setup-cluster:
	@[[ -n "$(shell kind get clusters | grep wegwijs)" ]] || kind create cluster --name wegwijs --kubeconfig deploy/skaffold/.kind-kubeconfig --config=deploy/skaffold/kind-config.yaml

k9s:
	k9s --kubeconfig deploy/skaffold/.kind-kubeconfig

develop: setup-cluster set-secret-values
	skaffold dev --profile dev --filename deploy/skaffold/skaffold.yaml --trigger=manual --status-check=false --kubeconfig=deploy/skaffold/.kind-kubeconfig

set-secret-values:
	cd deploy/skaffold && bash set-secret-values.sh

helm-dependency-update:
	helm dependency update deploy/helm/

test-templates:
	helm template test deploy/helm/ --dry-run --debug

psql:
	psql -p 5432 -h localhost -U user -d postgres

ingest-all: ingest-es ingest-case-law ingest-werk-instructie ingest-graphs

ingest-es:
	curl localhost:5000/system/create-es-indices && curl localhost:5000/system/ingest-es-from-blob-storage

ingest-case-law:
	curl localhost:5000/system/ingest-case-law-from-blob-storage

ingest-werk-instructie:
	curl localhost:5000/system/ingest-werk-instructie-from-blob-storage

ingest-graphs: ingest-jas ingest-taxonomy ingest-lido

ingest-jas:
	curl -XPOST -H "Content-Type: application/json" -d '{"blob_name": "JAS.ttl"}' localhost:5000/system/upload-graph

ingest-taxonomy:
	curl -XPOST -H "Content-Type: application/json" -d '{"blob_name": "Taxonomy.ttl"}' localhost:5000/system/upload-graph

ingest-lido:
	curl -XPOST -H "Content-Type: application/json" -d '{"blob_name": "lido.ttl"}' localhost:5000/system/upload-graph

ingest-selectielijsten:
	curl -XPOST -H "Content-Type: application/json" -d '{"file_name": "selectielijsten.csv"}' localhost:5000/system/upload-csv

test-pipeline: pipeline-test_1

pipeline-test_1:
	mkdir -p pipeline_data_outputs && curl -XPOST -H "Content-Type: application/json" -d '{"session_id": "1", "message": "Wanneer verwerkt de verwerkingsverantwoordelijke persoonsgegevens die niet reeds aan een geheimhoudingsplicht zijn onderworpen?"}' localhost:5000/pipeline > ./pipeline_data_outputs/output.txt && cat ./pipeline_data_outputs/output.txt | jq . > ./pipeline_data_outputs/output_1.json

# Code quality commands
.PHONY: lint format check-types install-hooks

lint:
	pre-commit run --all-files

format:
	pre-commit run black --all-files
	pre-commit run isort --all-files

check-types:
	pre-commit run mypy --all-files

install-hooks:
	pre-commit install
	pre-commit install --hook-type pre-push

# Development setup
setup-dev: install-hooks
	pip install -r requirements-dev.txt

# Scrapers
scrape-laws:
	python3 components/api/scrapers/law_scraper/law_scraper.py && python3 components/api/scrapers/law_scraper/divide_laws.py

scrape-case-law:
	python3 components/api/scrapers/case_law_scraper/case_law_scraper.py

scrape-werk-instructie:
	python3 components/api/scrapers/werk_instructie/clean_instructie.py

scrape-all: scrape-laws scrape-case-law scrape-werk-instructie
