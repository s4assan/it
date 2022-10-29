
common_tags = {
  "AssetID"       = "5980"
  "AssetName"     = "Insfrastructure"
  "Environment"   = "prod"
  "Project"       = "beta"
  "CreateBy"      = "Terraform"
  "cloudProvider" = "aws"
}
aws_region              = "us-east-2"
private_subnets_eks_ec2 = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnets_db      = ["10.0.3.0/24", "10.0.4.0/24"]
public                  = ["10.0.5.0/24", "10.0.6.0/24"]
aws_availability_zones  = ["us-east-2a", "us-east-2b"]

cidr_block                       = "10.0.0.0/16"
instance_tenancy                 = "default"
enable_dns_support               = true
enable_dns_hostnames             = true
enable_classiclink               = false
enable_classiclink_dns_support   = false
assign_generated_ipv6_cidr_block = false

cluster_name = "demo-cluster"
