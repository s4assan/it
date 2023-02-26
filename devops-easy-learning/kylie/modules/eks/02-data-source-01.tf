data "aws_vpc" "adl_eks_vpc" {
  filter {
    name   = "tag:Name"
    values = ["2560-dev-alpha-vpc"]
  }
}

data "aws_subnet" "eks_private_subnet_01" {
  filter {
    name   = "tag:Name"
    values = ["2560-dev-alpha-vpc-private-subnet-eks-ec2-02"]
  }
}


data "aws_subnet" "eks_private_subnet_02" {
  filter {
    name   = "tag:Name"
    values = ["2560-dev-alpha-vpc-private-subnet-eks-ec2-01"]
  }
}


data "aws_subnet" "eks_public_subnet_01" {
  filter {
    name   = "tag:Name"
    values = ["2560-dev-alpha-vpc-public-subnet-01"]
  }
}

data "aws_subnet" "eks_public_subnet_02" {
  filter {
    name   = "tag:Name"
    values = ["2560-dev-alpha-vpc-public-subnet-02"]
  }
}

