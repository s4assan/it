data "aws_vpc" "postgres_vpc" {
  filter {
    name   = "tag:Name"
    values = ["2560-dev-alpha-vpc"]
  }
}

data "aws_subnet" "db-subnet-private-01" {
  filter {
    name   = "tag:Name"
    values = ["2560-dev-alpha-vpc-private-subnet-db-01"]
  }
}

data "aws_subnet" "db-subnet-private-02" {
  filter {
    name   = "tag:Name"
    values = ["2560-dev-alpha-vpc-private-subnet-db-02"]
  }
}

# Get secret information for RDS password
data "aws_secretsmanager_secret" "rds_password" {
  name = "2568/alpha/db/databases-password"
}
data "aws_secretsmanager_secret_version" "rds_password" {
  secret_id = data.aws_secretsmanager_secret.rds_password.id
}

# Get secret information for RDS username
data "aws_secretsmanager_secret" "rds_username" {
  name = "2568/alpha/db/databases-username"
}
data "aws_secretsmanager_secret_version" "rds_username" {
  secret_id = data.aws_secretsmanager_secret.rds_username.id
}

/*
// CREATE A DATABASE WITH USERNAME AND PASSWORD
password = data.aws_secretsmanager_secret_version.rds_password.secret_string
username = data.aws_secretsmanager_secret_version.rds_username.secret_string
*/
