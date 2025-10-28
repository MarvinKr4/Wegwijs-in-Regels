CONTAINER:= api
PROJECT:= wegwijs
ifeq ($(origin VERSION),undefined)
VERSION:= develop
endif
ifeq ($(origin NAMESPACE),undefined)
NAMESPACE:= dev
endif
LOCAL_REPO:= localhost:32000
# REMOTE_REPO is not set by default. To push to a remote registry, set REMOTE_REPO when calling make, e.g.:
# make push-remote REMOTE_REPO=myregistry.example.com
IMAGE:=$(PROJECT)/$(NAMESPACE)/$(CONTAINER):$(VERSION)

help:
	@echo ''
	@echo 'Usage: make [TARGET] [EXTRA_ARGUMENTS]'
	@echo 'Targets:'
	@echo '  build    	build docker --image-- '
	@echo '  run  		run docker --image-- '
build:
	DOCKER_BUILDKIT=1 docker build --network=host --ssh default=$$SSH_AUTH_SOCK -t $(IMAGE) .
build-nc:
	DOCKER_BUILDKIT=1 docker build --no-cache --network=host --ssh default=$$SSH_AUTH_SOCK -t $(IMAGE) .
run:
	docker run -p 5000:5000 $(IMAGE)
run-bash:
	docker run -it -p 5000:5000 --entrypoint=/bin/bash $(IMAGE)
push-local:
	docker tag $(IMAGE) ${LOCAL_REPO}/$(IMAGE)
	docker push ${LOCAL_REPO}/$(IMAGE)
push-remote:
	@if [ -z "${REMOTE_REPO}" ]; then \
		echo "REMOTE_REPO is not set. Skipping push to remote."; \
	else \
		docker tag $(IMAGE) ${REMOTE_REPO}/$(IMAGE); \
		docker push ${REMOTE_REPO}/$(IMAGE); \
	fi
yeet: build push-remote


migrate:
	cd src && alembic upgrade head
make-migrations:
	cd src && alembic revision --autogenerate

# Scrapers
scrape-laws:
	python3 scrapers/law_scraper/law_scraper.py && python3 scrapers/law_scraper/divide_laws.py

scrape-case-law:
	python3 scrapers/case_law_scraper/case_law_scraper.py

scrape-werk-instructie:
	python3 scrapers/werk_instructie/clean_instructie.py

scrape-all: scrape-laws scrape-case-law scrape-werk-instructie
