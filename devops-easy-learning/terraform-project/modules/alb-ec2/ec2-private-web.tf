# # https://registry.terraform.io/modules/terraform-aws-modules/ec2-instance/aws/latest/examples/complete

module "ec2_private1" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "4.1.4"

  name                        = "web-server-01"
  ami                         = data.aws_ami.amzlinux2.id
  instance_type               = "t2.micro"
  key_name                    = "jenkins-key"
  monitoring                  = false
  associate_public_ip_address = true
  subnet_id                   = "subnet-0ae1f4115898aaacf"
  vpc_security_group_ids      = [aws_security_group.webserver-private-sg.id]
  user_data                   = file("${path.module}/user-data/web-servers.sh")
  user_data_replace_on_change = true
  tags = {
    Name = "web-server-01"
  }
}


module "ec2_private2" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "4.1.4"

  name                        = "web-server-02"
  ami                         = data.aws_ami.amzlinux2.id
  instance_type               = "t2.micro"
  key_name                    = "jenkins-key"
  monitoring                  = false
  associate_public_ip_address = true
  subnet_id                   = "subnet-0ae1f4115898aaacf"
  vpc_security_group_ids      = [aws_security_group.webserver-private-sg.id]
  user_data                   = file("${path.module}/user-data/web-servers.sh")
  user_data_replace_on_change = true
  tags = {
    Name = "web-server-02"
  }
}
