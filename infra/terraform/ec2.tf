# Use data source to retrieve a Debian 12 AMI
data "aws_ami" "debian" {
  most_recent = true

  filter {
    name   = "name"
    values = ["debian-12-amd64-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["136693071363"]
}

# launch ec2 instance and deploy Gaia with Docker Compose
resource "aws_instance" "ec2_instance" {
  ami                    = data.aws_ami.debian.id
  subnet_id              = aws_subnet.public_subnet_erik.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.webserver_security_group.id]
  user_data = templatefile("${path.module}/command.sh", {
    dockerhub_user  = var.dockerhub_user
    api_tag         = var.api_tag
    web_tag         = var.web_tag
    gaia_http_port  = var.gaia_http_port
    app_env_content = local.app_env_content_resolved
  })

  root_block_device {
    volume_size = var.root_volume_size_gb
    volume_type = "gp3"
  }

  tags = {
    Name = "web-instance"
  }

}
