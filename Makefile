.PHONY: help up up-local down logs build-apis build-web login push-apis push-web tf-init tf-plan tf-apply tf-destroy tf-output llm-install llm-run

# Docker Hub (override: make up DOCKERHUB_USER=otro API_TAG=v1)
DOCKERHUB_USER ?= eriktortarod
API_TAG ?= latest
WEB_TAG ?= latest
GAIA_HTTP_PORT ?= 8080
TF_DIR ?= infra/terraform
AWS_INSTANCE_TYPE ?= t3.medium
AWS_KEY_NAME ?= vockey
AWS_ROOT_VOLUME_SIZE_GB ?= 30
AWS_INGRESS_HTTP_CIDR ?= 0.0.0.0/0
AWS_INGRESS_SSH_CIDR ?= 0.0.0.0/0
APP_ENV_FILE ?= projects/api/.env

COMPOSE_ENV := DOCKERHUB_USER=$(DOCKERHUB_USER) API_TAG=$(API_TAG) WEB_TAG=$(WEB_TAG) GAIA_HTTP_PORT=$(GAIA_HTTP_PORT)
COMPOSE := $(COMPOSE_ENV) docker compose -f docker-compose.yml

## Stack Gaia (producción simulada)
help: ## Mostrar objetivos
	@echo "Gaia — Docker Compose (APIs desde Hub, web con nginx en :$(GAIA_HTTP_PORT))"
	@echo ""
	@echo "  make up          Pull APIs Hub + build frontend + arranque"
	@echo "  make up-local    Igual sin pull (tras make build-apis, usa tus imágenes locales)"
	@echo "  make down        Para y elimina contenedores"
	@echo "  make logs        Logs de los cuatro servicios"
	@echo "  make build-apis  Solo construir imágenes locales de las tres APIs (sin push)"
	@echo "  make build-web   Solo imagen del frontend"
	@echo "  make login       docker login Docker Hub"
	@echo "  make push-apis   build-apis + push a Docker Hub"
	@echo "  make push-web    Build + push frontend"
	@echo "  make tf-init     Inicializar Terraform en AWS"
	@echo "  make tf-plan     Ver plan Terraform (deploy Gaia en EC2)"
	@echo "  make tf-apply    Aplicar infraestructura y desplegar stack en AWS"
	@echo "  make tf-output   Mostrar URL/IP del despliegue"
	@echo "  make tf-destroy  Eliminar infraestructura AWS"
	@echo "  make llm-install Instalar dependencias del API plant_care_llm"
	@echo "  make llm-run     Ejecutar API local de plant_care_llm (puerto 5002)"
	@echo ""
	@echo "Variables: DOCKERHUB_USER API_TAG WEB_TAG GAIA_HTTP_PORT"
	@echo "AWS vars: TF_DIR AWS_INSTANCE_TYPE AWS_KEY_NAME AWS_ROOT_VOLUME_SIZE_GB AWS_INGRESS_HTTP_CIDR AWS_INGRESS_SSH_CIDR APP_ENV_FILE"

up: ## Pull APIs desde Hub (no las construye) + build frontend + http://localhost:$(GAIA_HTTP_PORT)
	$(COMPOSE) up -d --build --pull always

up-local: ## Sin pull: útil después de build-apis para probar imágenes locales sin subirlas
	$(COMPOSE) up -d --build --pull never

build-apis: ## Construir reconocimiento, cuidados y llm localmente (mismo tag que push-apis)
	docker build -f docker/plant-recognition-api/Dockerfile -t $(DOCKERHUB_USER)/gaia-plant-recognition-api:$(API_TAG) .
	docker build -f docker/plant-care-api/Dockerfile -t $(DOCKERHUB_USER)/gaia-plant-care-api:$(API_TAG) .
	docker build -f docker/plant-care-llm-api/Dockerfile -t $(DOCKERHUB_USER)/gaia-plant-care-llm-api:$(API_TAG) .

down: ## Parar stack
	$(COMPOSE) down

logs: ## Seguir logs
	$(COMPOSE) logs -f

build-web: ## Construir solo la imagen gaia-frontend
	$(COMPOSE) build frontend

login: ## Iniciar sesión en Docker Hub
	docker login -u $(DOCKERHUB_USER)

push-apis: build-apis ## Push de las imágenes ya construidas a $(DOCKERHUB_USER)/*:$(API_TAG)
	docker push $(DOCKERHUB_USER)/gaia-plant-recognition-api:$(API_TAG)
	docker push $(DOCKERHUB_USER)/gaia-plant-care-api:$(API_TAG)
	docker push $(DOCKERHUB_USER)/gaia-plant-care-llm-api:$(API_TAG)

push-web: build-web ## Build frontend y push a $(DOCKERHUB_USER)/gaia-frontend:$(WEB_TAG)
	docker push $(DOCKERHUB_USER)/gaia-frontend:$(WEB_TAG)

tf-init: ## Inicializar Terraform
	terraform -chdir=$(TF_DIR) init

tf-plan: ## Plan Terraform para desplegar Gaia en EC2 (imagenes Docker Hub)
	terraform -chdir=$(TF_DIR) plan \
		-var "dockerhub_user=$(DOCKERHUB_USER)" \
		-var "api_tag=$(API_TAG)" \
		-var "web_tag=$(WEB_TAG)" \
		-var "gaia_http_port=$(GAIA_HTTP_PORT)" \
		-var "instance_type=$(AWS_INSTANCE_TYPE)" \
		-var "root_volume_size_gb=$(AWS_ROOT_VOLUME_SIZE_GB)" \
		-var "key_name=$(AWS_KEY_NAME)" \
		-var "app_env_file_path=$(abspath $(APP_ENV_FILE))" \
		-var "ingress_http_cidr=$(AWS_INGRESS_HTTP_CIDR)" \
		-var "ingress_ssh_cidr=$(AWS_INGRESS_SSH_CIDR)"

tf-apply: ## Aplicar Terraform y desplegar stack Gaia en AWS
	terraform -chdir=$(TF_DIR) apply -auto-approve \
		-var "dockerhub_user=$(DOCKERHUB_USER)" \
		-var "api_tag=$(API_TAG)" \
		-var "web_tag=$(WEB_TAG)" \
		-var "gaia_http_port=$(GAIA_HTTP_PORT)" \
		-var "instance_type=$(AWS_INSTANCE_TYPE)" \
		-var "root_volume_size_gb=$(AWS_ROOT_VOLUME_SIZE_GB)" \
		-var "key_name=$(AWS_KEY_NAME)" \
		-var "app_env_file_path=$(abspath $(APP_ENV_FILE))" \
		-var "ingress_http_cidr=$(AWS_INGRESS_HTTP_CIDR)" \
		-var "ingress_ssh_cidr=$(AWS_INGRESS_SSH_CIDR)"

tf-output: ## Mostrar outputs del despliegue AWS
	terraform -chdir=$(TF_DIR) output

tf-destroy: ## Destruir infraestructura AWS
	terraform -chdir=$(TF_DIR) destroy -auto-approve \
		-var "dockerhub_user=$(DOCKERHUB_USER)" \
		-var "api_tag=$(API_TAG)" \
		-var "web_tag=$(WEB_TAG)" \
		-var "gaia_http_port=$(GAIA_HTTP_PORT)" \
		-var "instance_type=$(AWS_INSTANCE_TYPE)" \
		-var "root_volume_size_gb=$(AWS_ROOT_VOLUME_SIZE_GB)" \
		-var "key_name=$(AWS_KEY_NAME)" \
		-var "app_env_file_path=$(abspath $(APP_ENV_FILE))" \
		-var "ingress_http_cidr=$(AWS_INGRESS_HTTP_CIDR)" \
		-var "ingress_ssh_cidr=$(AWS_INGRESS_SSH_CIDR)"

llm-install: ## Instalar dependencias de projects/api/plant_care_llm (venv del repo)
	./venv/bin/python -m pip install -r projects/api/plant_care_llm/requirements.txt

llm-run: ## Ejecutar API plant_care_llm en local
	FLASK_DEBUG=false ./venv/bin/python projects/api/plant_care_llm/main.py
