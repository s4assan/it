source "amazon-ebs" "ubuntu" {
  ami_name = "jenkins-manster-{{timestamp}}"
  instance_type = "t3.medium"
  region        = "us-east-1"
  source_ami_filter {
    filters = {
      name                = "ubuntu/images/*ubuntu-xenial-16.04-amd64-server-*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["099720109477"]
  }
  ssh_username = "ubuntu"
  tags = {
    "Name"        = "jenkins-manster"
    "Environment" = "Production"
    "OS_Version"  = "Ubuntu"
    "Release"     = "Latest"
    "Created-by"  = "Packer"
  }
}

build {
  name = "jenkins-manster"
  sources = [
    "source.amazon-ebs.ubuntu"
  ]
  provisioner "file" {
    source = "./shell-scripts/jenkins-node.sh"
    destination = "/tmp/jenkins-node.sh"
  }
  provisioner "shell" {
    inline = [
      "sudo chmod +x /tmp/jenkins-node.sh",
      "sudo bash /tmp/jenkins-node.sh"
    ]
  }
}