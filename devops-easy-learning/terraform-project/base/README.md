

- https://github.com/leonardtia1/tia-devops/tree/main/Terraform/ek-tech-terraform/terraform-course/Merge-tags

- https://github.com/leonardtia1/tia-devops/blob/main/Terraform/ek-tech-terraform/terraform-course/zz01-Advance-topics/S3-with-region-accoount-id/main.tf

- https://github.com/leonardtia1/tia-devops/tree/main/Terraform/ek-tech-terraform/terraform-course/zz01-Advance-topics/asg-launch-config


## Merging 2 tags
- https://www.tinfoilcipher.co.uk/2021/05/05/terraform-applying-common-tags-to-resources-using-maps/

```s
resource "aws_instance" "private_node" {
    count                       = 10
    availability_zone           = data.aws_availability_zones.available.names[0]
    ami                         = data.aws_ami.tinfoil_ubuntu.id
    instance_type               = "t2.micro"
    key_name                    = "tinfoilkey"
    subnet_id                   = local.subnet_tinfoil_private
    vpc_security_group_ids      = [local.sg_tinfoil_private]
    tags = merge(var.default_tags,{
        Name = "Instance-${var.environment_name}${count.index}"
        },
    )
}


tags = merge(var.common_tags, {
    Name = format("%s-%s-%s-terraform-state", var.common_tags["AssetID"], var.common_tags["Environment"], var.common_tags["Project"])
    },
  )
```