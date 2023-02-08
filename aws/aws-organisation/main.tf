provider "aws" {
  region = "us-east-1"
}

resource "aws_organizations_organizational_unit" "DEL-DEV" {
  name      = "DEL-DEV"
  parent_id = "r-1fbqxxff"
}

resource "aws_organizations_organizational_unit" "DEL-PROD" {
  name      = "DEL-PROD"
  parent_id = "r-1fbqxxff"
}


resource "aws_organizations_policy" "example3" {
  name = "AWSFullAccess"

  content = <<CONTENT
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}

CONTENT
}


# https://registry.terraform.io/providers/hashicorp/aws/3.24.0/docs/resources/organizations_policy
resource "aws_organizations_policy" "example1" {
  name = "DenyDeleteS3"

  content = <<CONTENT
{
  "Version": "2012-10-17",
  "Statement": [
      {
          "Action": [
              "s3:DeleteBucket",
              "s3:DeleteObject",
              "s3:DeleteObjectVersion"
          ],
          "Resource": "*",
          "Effect": "Deny"
      }
  ]
}
CONTENT
}

resource "aws_organizations_policy" "example2" {
  name = "DenyLeavingOrganisation"

  content = <<CONTENT
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": [
        "organizations:LeaveOrganization"
      ],
      "Resource": "*"
    }
  ]
}
CONTENT
}


# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/organizations_policy_attachment
resource "aws_organizations_policy_attachment" "unit1" {
  policy_id = aws_organizations_policy.example1.id
  target_id = aws_organizations_organizational_unit.DEL-DEV.id
}

resource "aws_organizations_policy_attachment" "unit2" {
  policy_id = aws_organizations_policy.example2.id
  target_id = aws_organizations_organizational_unit.DEL-DEV.id
}

resource "aws_organizations_policy_attachment" "unit3" {
  policy_id = aws_organizations_policy.example3.id
  target_id = aws_organizations_organizational_unit.DEL-DEV.id
}
