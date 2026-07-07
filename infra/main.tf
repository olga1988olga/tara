terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    http = {
      source  = "hashicorp/http"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# Resolves to your current public IP at `terraform apply` time, so the
# security group tracks whichever network you're applying from.
data "http" "my_ip" {
  url = "https://checkip.amazonaws.com"
}

# Always resolves to the latest AWS-published PyTorch GPU DLAMI for the
# region, instead of a hardcoded AMI id that goes stale.
data "aws_ssm_parameter" "dlami_pytorch_gpu" {
  name = "/aws/service/deeplearning/ami/x86_64/oss-nvidia-driver-gpu-pytorch-2.7-ubuntu-22.04/latest/ami-id"
}

resource "aws_security_group" "tara" {
  name        = "tara-sg"
  description = "TARA dev instance security group"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.my_ip.response_body)}/32"]
  }

  # 443 (not 8000) - Caddy terminates TLS here and reverse-proxies to the
  # app internally; uvicorn itself is not exposed. Restricted to your IP -
  # this is where the actual app lives.
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.my_ip.response_body)}/32"]
  }

  # 80 open to everyone (not IP-restricted) - required for Let's Encrypt's
  # ACME HTTP-01 challenge/renewal, which connects from its own servers, not
  # yours. Only ever serves ACME challenges + a redirect to HTTPS, nothing
  # sensitive, so this is safe to leave open.
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_key_pair" "tara" {
  key_name   = "tara-key"
  public_key = file(var.public_key_path)
}

resource "aws_instance" "tara" {
  ami                    = data.aws_ssm_parameter.dlami_pytorch_gpu.value
  instance_type          = var.instance_type
  key_name               = aws_key_pair.tara.key_name
  vpc_security_group_ids = [aws_security_group.tara.id]

  root_block_device {
    volume_size = var.root_volume_size
  }

  user_data = templatefile("${path.module}/bootstrap.sh.tftpl", {
    tara_repo_url = var.tara_repo_url
  })
  user_data_replace_on_change = true

  tags = {
    Name = "tara-${var.instance_type}"
  }
}

output "public_ip" {
  value = aws_instance.tara.public_ip
}

output "instance_id" {
  value = aws_instance.tara.id
}
