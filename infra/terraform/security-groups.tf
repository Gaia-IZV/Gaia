# create security group for the web server
# terraform aws create security group
resource "aws_security_group" "webserver_security_group" {
  name        = "web-sg"
  description = "enable http/https access on port 80/443 via alb sg and access on port 22 via ssh sg"
  vpc_id      = aws_vpc.vpc.id

  ingress {
    description = "frontend http access"
    from_port   = var.gaia_http_port
    to_port     = var.gaia_http_port
    protocol    = "tcp"
    cidr_blocks = [var.ingress_http_cidr]
  }


  ingress {
    description = "ssh access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ingress_ssh_cidr]
  }
  ingress {
    description = "https access"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.ingress_http_cidr]
  }

  ingress {
    description = "plant recognition api access"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = [var.ingress_http_cidr]
  }

  ingress {
    description = "plant care api access"
    from_port   = 5001
    to_port     = 5001
    protocol    = "tcp"
    cidr_blocks = [var.ingress_http_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "web-sg"
  }
}
