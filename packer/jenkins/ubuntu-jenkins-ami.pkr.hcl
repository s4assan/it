
source "amazon-ebs" "ubuntu-jenkins" {
  ami_name      = "${var.ami_name}-${regex_replace(timestamp(), "[- TZ:]", "")}"
  instance_type = var.instance_type
  region        = var.ami_regions
  source_ami_filter {
    filters = {
      name                = format("ubuntu/images/hvm-ssd/ubuntu-*-20.04-%s-server-*", var.architecture)
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["099720109477"]
  }
  ssh_username = "ubuntu"
  # subnet_id    = var.vpc_id
  # vpc_id       = var.subnet_id
  vpc_id    = "vpc-068852590ea4b093b"
  subnet_id = "subnet-096d45c28d9fb4c14"
  tags      = var.tags
}

build {
  name = "ubuntu-jenkins"
  sources = [
    "source.amazon-ebs.ubuntu-jenkins"
  ]
  provisioner "shell" {
    inline = [
      
    ]
  }
}

