output "ec2_public_ip" {
  description = "IP publica de la instancia Gaia"
  value       = aws_instance.ec2_instance.public_ip
}

output "gaia_url" {
  description = "URL del frontend desplegado"
  value       = "http://${aws_instance.ec2_instance.public_ip}:${var.gaia_http_port}"
}

output "ssh_hint" {
  description = "Comando de ejemplo para acceder por SSH"
  value       = "ssh -i <ruta-a-${var.key_name}.pem> ${var.ssh_user}@${aws_instance.ec2_instance.public_ip}"
}
