.PHONY: help build-all build-n8n build-plant-api run-plant-api stop-plant-api rm-plant-api push-plant-api login-dockerhub stop-n8n start-n8n rm-n8n

# Docker Hub (override: make push-plant-api DOCKERHUB_USER=otro PLANT_API_TAG=v1)
DOCKERHUB_USER ?= eriktortarod
PLANT_API_TAG ?= latest

## General
build-all: ## Build all containers
	@make build-n8n

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
