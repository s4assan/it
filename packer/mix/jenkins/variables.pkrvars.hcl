ami_name      = "jenkins"
ami_regions   = "us-east-1"
instance_type = "t2.micro"
# vpc_id        = "vpc-068852590ea4b093b"
# subnet_id     = "subnet-096d45c28d9fb4c14"

tags = {
  "Name"        = "jenkins-aws-ami"
  "Environment" = "Production"
  "Release"     = "Latest"
  "Created-by"  = "Packer"
}