.PHONY: help up down logs build-web login push-apis push-web

# Docker Hub (override: make up DOCKERHUB_USER=otro API_TAG=v1)
DOCKERHUB_USER ?= eriktortarod
API_TAG ?= latest
WEB_TAG ?= latest
GAIA_HTTP_PORT ?= 8080

COMPOSE_ENV := DOCKERHUB_USER=$(DOCKERHUB_USER) API_TAG=$(API_TAG) WEB_TAG=$(WEB_TAG) GAIA_HTTP_PORT=$(GAIA_HTTP_PORT)
COMPOSE := $(COMPOSE_ENV) docker compose -f docker-compose.yml

## Stack Gaia (producción simulada)
help: ## Mostrar objetivos
	@echo "Gaia — Docker Compose (APIs desde Hub, web con nginx en :$(GAIA_HTTP_PORT))"
	@echo ""
	@echo "  make up          Levanta todo (pull APIs, build frontend si hace falta)"
	@echo "  make down        Para y elimina contenedores"
	@echo "  make logs        Logs de los tres servicios"
	@echo "  make build-web   Solo imagen del frontend"
	@echo "  make login       docker login Docker Hub"
	@echo "  make push-apis   Build local + push reconocimiento y cuidados"
	@echo "  make push-web    Build + push frontend"
	@echo ""
	@echo "Variables: DOCKERHUB_USER API_TAG WEB_TAG GAIA_HTTP_PORT"

up: ## Pull imágenes Hub + build frontend + arranque en http://localhost:$(GAIA_HTTP_PORT)
	$(COMPOSE) up -d --build --pull always

down: ## Parar stack
	$(COMPOSE) down

logs: ## Seguir logs
	$(COMPOSE) logs -f

build-web: ## Construir solo la imagen gaia-frontend
	$(COMPOSE) build frontend

login: ## Iniciar sesión en Docker Hub
	docker login -u $(DOCKERHUB_USER)

push-apis: ## Build local de ambas APIs y push a $(DOCKERHUB_USER)/*:$(API_TAG)
	docker build -f docker/plant-recognition-api/Dockerfile -t $(DOCKERHUB_USER)/gaia-plant-recognition-api:$(API_TAG) .
	docker build -f docker/plant-care-api/Dockerfile -t $(DOCKERHUB_USER)/gaia-plant-care-api:$(API_TAG) .
	docker push $(DOCKERHUB_USER)/gaia-plant-recognition-api:$(API_TAG)
	docker push $(DOCKERHUB_USER)/gaia-plant-care-api:$(API_TAG)

push-web: build-web ## Build frontend y push a $(DOCKERHUB_USER)/gaia-frontend:$(WEB_TAG)
	docker push $(DOCKERHUB_USER)/gaia-frontend:$(WEB_TAG)
