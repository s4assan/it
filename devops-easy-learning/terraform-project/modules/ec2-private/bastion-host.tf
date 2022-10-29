# EC2 Instance
resource "aws_instance" "bastion" {
  depends_on = [
    aws_security_group.ssh_http_sg
  ]
  ami                    = data.aws_ami.amzlinux2.id
  instance_type          = "t2.micro"
  key_name               = "jenkins-key"
  vpc_security_group_ids = [aws_security_group.ssh_http_sg.id]
  subnet_id              = data.aws_subnet.private_subnet.id
  tags = {
    "Name" = "ec2-private"
  }
}

