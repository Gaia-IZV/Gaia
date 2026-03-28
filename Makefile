.PHONY: help build-all build-n8n build-plant-api build-plant-care-api run-plant-api run-plant-care-api \
	start-apis stop-plant-api stop-plant-care-api rm-plant-api rm-plant-care-api push-plant-api push-plant-care-api \
	serve-frontend login-dockerhub stop-n8n start-n8n rm-n8n

# Docker Hub (override: make push-plant-api DOCKERHUB_USER=otro PLANT_API_TAG=v1)
DOCKERHUB_USER ?= eriktortarod
PLANT_API_TAG ?= latest
PLANT_CARE_API_TAG ?= latest

## General
build-all: ## Build all containers
	@make build-n8n

serve-frontend: ## Chat de prueba en http://localhost:8080 (con las APIs en 5000 y 5001 arrancadas)
	cd projects/frontend && python -m http.server 8080

help: ## Display this help message
	@echo "Available commands:"
	@awk 'BEGIN {FS=":.*## "; category=""} \
		/^## [^#]/ { \
			if (category) printf "\n"; \
			category=$$0; gsub(/^## /, "", category); \
			printf "\033[1m%s:\033[0m\n", category; \
			next \
		} \
		/^[[:space:]]*[a-zA-Z0-9_-]+:.*## / { \
			printf "  \033[36m%-28s\033[0m %s\n", $$1, $$2 \
		}' $(MAKEFILE_LIST)

## n8n
build-n8n: ## Build and start n8n workflow container
	@echo "Building n8n image..."
	cd docker && docker build -f Dockerfile.n8n -t n8n .
	@echo "Starting n8n container..."
	docker run -d \
		--name n8n \
		-p 5678:5678 \
		-v ~/.n8n:/home/node/.n8n \
		n8n
	@echo "n8n running at http://localhost:5678"

start-n8n: ## Start existing n8n container
	@docker start n8n 

stop-n8n: ## Stop n8n container
	@docker stop n8n

rm-n8n: ## Stop and remove n8n container
	@docker rm n8n

## Plant recognition API
build-plant-api: ## Build plant recognition API image
	docker build -f docker/plant-recognition-api/Dockerfile -t gaia-plant-recognition-api .

run-plant-api: ## Run plant recognition API on port 5000 (uses projects/api/.env if the file exists)
	docker run --rm -d \
		--name gaia-plant-api \
		-p 5000:5000 \
		$$(test -f projects/api/.env && echo "--env-file projects/api/.env") \
		gaia-plant-recognition-api

stop-plant-api: ## Stop plant recognition API container
	@docker stop gaia-plant-api

rm-plant-api: ## Stop and remove plant recognition API container
	@docker rm -f gaia-plant-api 2>/dev/null || true

login-dockerhub: ## Log in to Docker Hub (run once per machine / when token expires)
	docker login -u $(DOCKERHUB_USER)

push-plant-api: build-plant-api ## Build, tag, and push plant API (DOCKERHUB_USER=$(DOCKERHUB_USER), PLANT_API_TAG)
	docker tag gaia-plant-recognition-api:latest $(DOCKERHUB_USER)/gaia-plant-recognition-api:$(PLANT_API_TAG)
	docker push $(DOCKERHUB_USER)/gaia-plant-recognition-api:$(PLANT_API_TAG)

## Plant care API (semantic search over cuidados_plantas.csv, port 5001)
build-plant-care-api: ## Build plant care / semantic search API image
	docker build -f docker/plant-care-api/Dockerfile -t gaia-plant-care-api .

run-plant-care-api: ## Run plant care API on port 5001 (optional projects/api/.env)
	docker run --rm -d \
		--name gaia-plant-care-api \
		-p 5001:5001 \
		$$(test -f projects/api/.env && echo "--env-file projects/api/.env") \
		gaia-plant-care-api

stop-plant-care-api: ## Stop plant care API container
	@docker stop gaia-plant-care-api

rm-plant-care-api: ## Stop and remove plant care API container
	@docker rm -f gaia-plant-care-api 2>/dev/null || true

push-plant-care-api: build-plant-care-api ## Build, tag, and push plant care API (PLANT_CARE_API_TAG)
	docker tag gaia-plant-care-api:latest $(DOCKERHUB_USER)/gaia-plant-care-api:$(PLANT_CARE_API_TAG)
	docker push $(DOCKERHUB_USER)/gaia-plant-care-api:$(PLANT_CARE_API_TAG)

start-apis: rm-plant-api rm-plant-care-api ## Run recognition (5000) + plant care (5001); build images first if needed
	docker run --rm -d \
		--name gaia-plant-api \
		-p 5000:5000 \
		$$(test -f projects/api/.env && echo "--env-file projects/api/.env") \
		gaia-plant-recognition-api
	docker run --rm -d \
		--name gaia-plant-care-api \
		-p 5001:5001 \
		$$(test -f projects/api/.env && echo "--env-file projects/api/.env") \
		gaia-plant-care-api
	@echo "Recognition API: http://localhost:5000  |  Plant care API: http://localhost:5001"
