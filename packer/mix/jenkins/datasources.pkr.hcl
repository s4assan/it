# # Data sources are always treated BEFORE locals and sources.
# data "amazon-ami" "ubuntu-20_04" {
#   filters = {
#     name                = format("ubuntu/images/hvm-ssd/ubuntu-*-20.04-%s-server-*", var.architecture)
#     root-device-type    = "ebs"
#     virtualization-type = "hvm"
#   }
#   most_recent = true
#   owners      = ["099720109477"]
#   region      = var.ami_regions
# }