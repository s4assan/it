# https://registry.terraform.io/modules/terraform-aws-modules/alb/aws/latest


# Terraform AWS Application Load Balancer (ALB)
module "alb" {
  source = "terraform-aws-modules/alb/aws"
  #   version = "5.16.0"
  version = "8.1.0"

  name                       = "webserver-alb"
  internal                   = false
  enable_deletion_protection = false
  load_balancer_type         = "application"
  vpc_id                     = "vpc-0b494f9d07c3b9849"
  security_groups            = [aws_security_group.alb-webserver-sg.id]
  subnets = [
    "subnet-0582e922025ad5306",
    "subnet-0b7759c62d4566943"
  ]

  # Listeners
  http_tcp_listeners = [{
    port               = 80
    protocol           = "HTTP"
    target_group_index = 0
    action_type        = "redirect"
    redirect = {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
    }
  ]

  https_listeners = [{
    port               = 443
    protocol           = "HTTPS"
    certificate_arn    = "arn:aws:acm:us-east-1:788210522308:certificate/46157f3b-7efb-49dd-ad8a-fc94edb81724"
    target_group_index = 0
  }]

  # Target Groups
  target_groups = [{
    backend_protocol     = "HTTP"
    backend_port         = 80
    target_type          = "instance"
    deregistration_delay = 10
    health_check = {
      enabled             = true
      interval            = 30
      path                = "/index.html"
      port                = "traffic-port"
      healthy_threshold   = 3
      unhealthy_threshold = 3
      timeout             = 6
      protocol            = "HTTP"
      matcher             = "200"
    }

    # Target Group
    targets = {
      my_app1_vm1 = {
        target_id = module.ec2_private1.id
        port      = 80
      },
      my_app1_vm2 = {
        target_id = module.ec2_private2.id
        port      = 80
      }
    }
    tags = { # Target Group Tags
      Name = "Websers-alb"
    }
  }]
  tags = { # ALB Tags
    Name = "Websers-target-group"
  }
}
