variable "region" {
  default = "eu-north-1"
}

variable "public_key_path" {
  default = "~/.ssh/id_ed25519.pub"
}

variable "instance_type" {
  # Cheap default so a plain `terraform apply` never accidentally bills GPU
  # hours. Override for real training: -var="instance_type=g4dn.xlarge"
  # (T4, 16GB VRAM) - note this needs an EC2 "G and VT instances" vCPU quota
  # increase on fresh accounts, and is NOT covered by AWS Activate/credit
  # grants that exclude GPU instance types.
  default = "t3.micro"
}

variable "root_volume_size" {
  # AMI snapshot is 40GB (verified via `aws ec2 describe-images`) - that's the
  # hard floor. 50GB gives headroom for the cheap smoke-test profile; bump
  # via -var/tfvars for real work with model/dataset caches (see gpu.tfvars.example).
  default = 50
}

variable "tara_repo_url" {
  default = "https://github.com/olga1988olga/tara.git"
}
