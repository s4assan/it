

source "amazon-ebs" "ubuntu" {
  ami_name                    = "jenkins-node-bastion-{{timestamp}}"
  ami_description             = "jenkins-node-bastion"
  associate_public_ip_address = false
  force_delete_snapshot       = true
  force_deregister            = true
  instance_type               = "t3.medium"
  region                      = "us-east-1"
  vpc_id                      = "vpc-068852590ea4b093b"
  subnet_id                   = "subnet-096d45c28d9fb4c14"
  # source_ami                  = data.amazon-ami.ubuntu_20_04.id

  source_ami_filter {
    filters = {
      name                = "ubuntu/images/hvm-ssd/*ubuntu-*${var.release}-amd64-server*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["099720109477"]
  }
  ssh_clear_authorized_keys = "true"
  ssh_keep_alive_interval   = "15s"
  ssh_pty                   = "true"
  ssh_timeout               = "10m"
  ssh_username              = "ubuntu"

  tags = {
    "Name"        = "MyUbuntuImage"
    "Environment" = "Production"
    "OS_Version"  = "Ubuntu"
    "Release"     = "Latest"
    "Created-by"  = "Packer"
  }
}

build {
  name = "jenkins-node-bastion"
  sources = [
    "source.amazon-ebs.ubuntu"
  ]
  provisioner "file" {
    source      = "./shell-scripts/jenkins-node.sh"
    destination = "/tmp/jenkins-node.sh"
  }
  # provisioner "shell" {
  #   inline = [
  #     "sudo chmod +x /tmp/jenkins-node.sh",
  #     "sudo bash /tmp/jenkins-node.sh"
  #   ]
  # }
}



























# source "amazon-ebs" "ubuntu" {
#   ami_name                    = "jenkins-node-bastion-{{timestamp}}"
#   ami_description             = "jenkins-node-bastion"
#   associate_public_ip_address = false
#   force_delete_snapshot       = true
#   force_deregister            = true
#   instance_type               = "t3.medium"
#   region                      = "us-east-1"
#   vpc_id                      = "vpc-068852590ea4b093b"
#   subnet_id                   = "subnet-096d45c28d9fb4c14"
#   source_ami                  = "ami-00874d747dde814fa"
#   ssh_username                = "ubuntu"

#   # source_ami_filter {
#   #   filters = {
#   #     # name                = "ubuntu/images/*ubuntu-xenial-16.04-amd64-server-*"
#   #     name                = "ubuntu/images/hvm-ssd/ubuntu-bionic-20.04-amd64-server-*"
#   #     architecture        = "x86_64"
#   #     block-device-mapping.volume-type =  "gp2"
#   #     root-device-type    = "ebs"
#   #     virtualization-type = "hvm"
#   #   }
#   #   most_recent = true
#   #   owners      = ["099720109477"]
#   # }

#   tags = {
#     "Name"        = "MyUbuntuImage"
#     "Environment" = "Production"
#     "OS_Version"  = "Ubuntu"
#     "Release"     = "Latest"
#     "Created-by"  = "Packer"
#   }
# }

# build {
#   name = "jenkins-node-bastion"
#   sources = [
#     "source.amazon-ebs.ubuntu"
#   ]
#   provisioner "file" {
#     source      = "./shell-scripts/jenkins-node.sh"
#     destination = "/tmp/jenkins-node.sh"
#   }
#   # provisioner "shell" {
#   #   inline = [
#   #     "sudo chmod +x /tmp/jenkins-node.sh",
#   #     "sudo bash /tmp/jenkins-node.sh"
#   #   ]
#   # }
# }