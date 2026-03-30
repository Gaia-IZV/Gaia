resource "null_resource" "sync_env_file" {
  count = (local.app_env_file_exists && var.ssh_private_key_path != "" && var.key_name != null) ? 1 : 0

  triggers = {
    instance_id = aws_instance.ec2_instance.id
    env_hash    = sha256(local.app_env_content_resolved)
  }

  connection {
    type        = "ssh"
    user        = var.ssh_user
    host        = aws_instance.ec2_instance.public_ip
    private_key = file(var.ssh_private_key_path)
    timeout     = "4m"
  }

  provisioner "file" {
    source      = var.app_env_file_path
    destination = "/tmp/gaia.env"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo mkdir -p /opt/gaia",
      "sudo mv /tmp/gaia.env /opt/gaia/.env",
      "sudo chown root:root /opt/gaia/.env",
      "cd /opt/gaia && sudo docker compose pull plant-recognition plant-care && sudo docker compose up -d plant-recognition plant-care"
    ]
  }
}
