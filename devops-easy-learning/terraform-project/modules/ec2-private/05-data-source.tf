data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Name"
    values = ["2560-dev-alpha-vpc"]
  }
}

data "aws_subnet" "private_subnet" {
  filter {
    name   = "tag:Name"
    values = ["2560-dev-alpha-vpc-private-subnet-eks-ec2-01"]
  }
}


