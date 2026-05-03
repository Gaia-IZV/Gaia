#!/bin/bash
set -euxo pipefail

export DEBIAN_FRONTEND=noninteractive

# Add swap to avoid OOM on small lab instances when loading ML models.
if ! swapon --show | grep -q '/swapfile'; then
  fallocate -l 4G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=4096
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  grep -q '^/swapfile ' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

apt-get update -y
apt-get install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  > /etc/apt/sources.list.d/docker.list
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
apt-get clean
rm -rf /var/lib/apt/lists/*
systemctl enable --now docker

mkdir -p /opt/gaia
cd /opt/gaia

cat > .env <<'ENV_FILE'
${app_env_content}
ENV_FILE

cat > docker-compose.yml <<EOF
name: gaia

services:
  plant-recognition:
    image: ${dockerhub_user}/gaia-plant-recognition-api:${api_tag}
    pull_policy: always
    env_file:
      - .env
    environment:
      - HF_HUB_DOWNLOAD_TIMEOUT=120
      - HF_HUB_ETAG_TIMEOUT=120
    expose:
      - "5000"
    restart: unless-stopped

  plant-care:
    image: ${dockerhub_user}/gaia-plant-care-api:${api_tag}
    pull_policy: always
    env_file:
      - .env
    expose:
      - "5001"
    restart: unless-stopped

  plant-care-llm:
    image: ${dockerhub_user}/gaia-plant-care-llm-api:${api_tag}
    pull_policy: always
    env_file:
      - .env
    expose:
      - "5002"
    restart: unless-stopped

  frontend:
    image: ${dockerhub_user}/gaia-frontend:${web_tag}
    pull_policy: always
    ports:
      - "${gaia_http_port}:80"
    depends_on:
      - plant-recognition
      - plant-care
      - plant-care-llm
    restart: unless-stopped
EOF

docker compose -f docker-compose.yml pull
docker compose -f docker-compose.yml up -d