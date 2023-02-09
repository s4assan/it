provider "aws" {
  region  = "us-east-1"
  version = ">=2.8,<=2.30"
}
resource "aws_s3_bucket" "terraform_s3" {
  bucket = "terraform-bucket-232"
  acl    = "private"
}
