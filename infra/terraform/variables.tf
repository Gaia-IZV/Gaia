variable "vpc_cidr_block" {
  description = "CIDR block para la VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_cidr_block" {
  description = "CIDR block para la Subnet Pública"
  type        = string
  default     = "10.0.0.0/24"
}

variable "availability_zone" {
  description = "Zona de disponibilidad para la Subnet Pública"
  type        = string
  default     = "us-east-1a"
}

variable "region" {
  description = "Región para el proveedor de AWS"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "Tipo de instancia EC2"
  type        = string
  default     = "t3.medium"
}

variable "root_volume_size_gb" {
  description = "Tamano del volumen raiz de EC2 en GB"
  type        = number
  default     = 30
}

variable "key_name" {
  description = "Nombre del key pair de EC2 para acceso SSH"
  type        = string
  default     = "vockey"
}

variable "ssh_user" {
  description = "Usuario SSH de la AMI Debian"
  type        = string
  default     = "admin"
}

variable "ssh_private_key_path" {
  description = "Ruta absoluta a la llave privada SSH (vockey) para provisioners"
  type        = string
  default     = ""
}

variable "ingress_http_cidr" {
  description = "CIDR para acceso HTTP (puerto 80)"
  type        = string
  default     = "0.0.0.0/0"
}

variable "ingress_ssh_cidr" {
  description = "CIDR para acceso SSH (puerto 22)"
  type        = string
  default     = "0.0.0.0/0"
}

variable "dockerhub_user" {
  description = "Usuario de Docker Hub dueño de las imagenes de Gaia"
  type        = string
  default     = "eriktortarod"
}

variable "api_tag" {
  description = "Tag para las imagenes de APIs"
  type        = string
  default     = "latest"
}

variable "web_tag" {
  description = "Tag para la imagen de frontend"
  type        = string
  default     = "latest"
}

variable "gaia_http_port" {
  description = "Puerto expuesto por el frontend en EC2"
  type        = number
  default     = 80
}

variable "app_env_content" {
  description = "Contenido del archivo .env para las APIs (multilinea)"
  type        = string
  default     = <<-EOT
USING_MONGO=false
USING_S3=false
HF_TOKEN=
GROQ_API_KEY=
GROQ_KEY=
MONGO_USER_NAME=
MONGO_USER_PASSWORD=
MONGO_CONECTION_STRING=
S3_BUCKET_NAME=
EOT
}

variable "app_env_file_path" {
  description = "Ruta local al .env a copiar a EC2 (si existe, tiene prioridad)"
  type        = string
  default     = "../../projects/api/.env"
}
