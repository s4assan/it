## Reference link
- https://www.youtube.com/@awstraining
- https://www.youtube.com/watch?v=jtKqYM9GjNM
- https://github.com/iaasacademy/aws-how-to-guide

## prevent-leaving-org
- This should be created in the AWS management account
- Atach the policy to a specify OU so that they will not be able to leave the organinsation. Other account can leave the organisation by default
```json
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
```

## Create a cross account access role between the management account and the members account
- AWS-DEV-ASSUME-REOLE
- AWS-PROD-ASSUME-REOLE
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::788210522308:root"
            },
            "Action": "sts:AssumeRole",
            "Condition": {}
        }
    ]
}
```

## Permission Boundry
```json
{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "AllowAdminAccess",
        "Effect": "Allow",
        "Action": "*",
        "Resource": "*"
      },
      {
        "Sid": "DenyAccessToCostAndBilling",
        "Effect": "Deny",
        "Action": [
          "account:*",
          "aws-portal:*",
          "savingsplans:*",
          "cur:*",
          "ce:*"
      ],
      "Resource": "*"
     },
     {
       "Sid": "DenyPermBoundaryIAMPolicyAlteration",
       "Effect": "Deny",
       "Action": [
         "iam:DeletePolicy",
         "iam:DeletePolicyVersion",
         "iam:CreatePolicyVersion",
         "iam:SetDefaultPolicyVersion"
     ],
     "Resource": [
       "arn:aws:iam::788210522308:policy/ScopePermissions"
     ]
    },
    {
      "Sid": "DenyRemovalOfPermBoundaryFromAnyUserOrRole",
      "Effect": "Deny",
      "Action": [
        "iam:DeleteUserPermissionsBoundary",
        "iam:DeleteRolePermissionsBoundary"
     ],
     "Resource": [
       "arn:aws:iam::788210522308:user/*",
       "arn:aws:iam::788210522308:role/*"
     ],
     "Condition": {
       "StringEquals": {
         "iam:PermissionsBoundary": "arn:aws:iam::788210522308:policy/ScopePermissions"
       }
      }
     },
     {
       "Sid": "DenyAccessIfRequiredPermBoundaryIsNotBeingApplied",
       "Effect": "Deny",
       "Action": [
       "iam:PutUserPermissionsBoundary",
       "iam:PutRolePermissionsBoundary"
     ],
     "Resource": [
       "arn:aws:iam::788210522308:user/*",
       "arn:aws:iam::788210522308:role/*"
     ],
     "Condition": {
       "StringNotEquals": {
         "iam:PermissionsBoundary": "arn:aws:iam::788210522308:policy/ScopePermissions"
       }
      }
    },
    {
      "Sid": "DenyUserAndRoleCreationWithOutPermBoundary",
      "Effect": "Deny",
      "Action": [
        "iam:CreateUser",
        "iam:CreateRole"
    ],
    "Resource": [
      "arn:aws:iam::788210522308:user/*",
      "arn:aws:iam::788210522308:role/*"
    ],
    "Condition": {
      "StringNotEquals": {
        "iam:PermissionsBoundary": "arn:aws:iam::788210522308:policy/ScopePermissions"
      }
     }
   },
   {
     "Sid": "DenyIAMActions",
     "Effect": "Deny",
     "Action": "iam:PassRole",
     "Resource": "arn:aws:iam::788210522308:role/*"
    }
   ]
  }
  ```


## AWS PROFILE
```
[default]
aws_access_key_id = AKIA3PBICDDCIA3PBICDDCHAPBJHAPBJ7DZ
aws_secret_access_key = r1E4yAM0QSZjSq8TlrSRpFtEws39+sLu0QSZjSq8TlrSRpFtEws3pY+xcnP2


[ADFS-AWS-ReadOnly]
region = us-east-1
source_profile = default
role_arn = arn:aws:iam::XXXXXXXXXXXXXXXX:role/AWS-ReadOnly-Role

[ADFS-AWS-Admins]
region = us-east-1
source_profile = default
role_arn = arn:aws:iam::XXXXXXXXXXXXXXXX:role/AWS-Admin-Role

[ADFS-EKS-Admins]
region = us-east-1
source_profile = default
role_arn = arn:aws:iam::XXXXXXXXXXXXXXXX:role/AWS-EKS-Admin-Role

[awsadmin]
region = us-east-1
aws_access_key_id = AKIA3PBIA3PBICDDCHAPBJICDDCB273DI6T
aws_secret_access_key = aPqUVNjcia4alZRQpJn0QSZjSq8TlrSRpFtEws3aeaogu8Odd/TNWxzuAI2L

[awseksadmin]
region = us-east-1
aws_access_key_id = AKIA3PBICDIA3PBICDDCHAPBJDCKJEV7CGL
aws_secret_access_key = rQyr1HV4ztKrhn0QSZjSq8TlrSRpFtEws3Qpfs0krklTTCCr1nX+Em0eP39S

[awsreadonly]
region = us-east-1
aws_access_key_id = AKIA3PBICDDCJW46WLHK
aws_secret_access_key = XqdoehqqNz0QSZjSq8TlrSRpFtEws31XgTyF2bVzFlNOqioZL1CRqfdbL7gv


[dev]
region = us-east-1
source_profile = default
role_arn = arn:aws:iam::XXXXXXXXXXXXXXXX:role/AWS-DEV-ASSUME-REOLE

[prod]
region = us-east-1
source_profile = default
role_arn = arn:aws:iam::XXXXXXXXXXXXXXXX:role/AWS-PROD-ASSUME-REOLE
```