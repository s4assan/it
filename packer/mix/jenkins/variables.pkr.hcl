variable "ami_name" {
  type    = string
  default = "jenkins"
}

variable "ami_regions" {
  type    = string
  default = "us-east-1"
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "tags" {
  type = map(string)
  default = {
    "Name"        = "jenkins-aws-ami"
    "Environment" = "Production"
    "Release"     = "Latest"
    "Created-by"  = "Packer"
  }
}

# variable "vpc_id" {
#   type    = string
#   default = "vpc-068852590ea4b093b"
# }

# variable "subnet_id" {
#   type    = string
#   default = "subnet-096d45c28d9fb4c14"
# }

variable "architecture" {
  type        = string
  description = "CPU architecture ID of the build with the following possible values: [amd64 (default), arm64]"
  default     = "amd64"
}