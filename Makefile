.PHONY: help build-all build-n8n stop-n8n start-n8n rm-n8n

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
