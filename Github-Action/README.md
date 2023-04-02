## GitHub Actions
- https://www.youtube.com/watch?v=RCpo7qaHhTQ
- Docker containers with GitHub Actions [here](https://www.youtube.com/watch?v=09lZdSpeHAk)
- GitHub link [here](https://github.com/marcel-dempers/docker-development-youtube-series/tree/master/.github/workflows)


```yml
name: Docker Series Builds

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    # runs-on: [self-hosted, linux]
    steps:
    - uses: actions/checkout@v2
    - name: docker login
      env:
        DOCKER_USER: ${{ secrets.DOCKER_USER }}   
        DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}  
      run: |
        docker login -u $DOCKER_USER -p $DOCKER_PASSWORD
    - name: docker build csharp
      run: |
        docker build ./c# -t aimvector/csharp:1.0.0
    - name: docker build nodejs
      run: |
        docker build ./nodejs -t aimvector/nodejs:1.0.0
    - name: docker build python
      run: |
        docker build ./python -t aimvector/python:1.0.0
    - name: docker build golang
      run: |
        docker build ./golang -t aimvector/golang:1.0.0
    - name: docker push
      run: |
        docker push aimvector/csharp:1.0.0
        docker push aimvector/nodejs:1.0.0
        docker push aimvector/golang:1.0.0
        docker push aimvector/python:1.0.0


name: GitHub Actions Demo
run-name: ${{ github.actor }} is testing out GitHub Actions 🚀
on: [push]
jobs:
  Explore-GitHub-Actions:
    runs-on: ubuntu-latest
    steps:
      - run: echo "🎉 The job was automatically triggered by a ${{ github.event_name }} event."
      - run: echo "🐧 This job is now running on a ${{ runner.os }} server hosted by GitHub!"
      - run: echo "🔎 The name of your branch is ${{ github.ref }} and your repository is ${{ github.repository }}."
      - name: Check out repository code
        uses: actions/checkout@v3
      - run: echo "💡 The ${{ github.repository }} repository has been cloned to the runner."
      - run: echo "🖥️ The workflow is now ready to test your code on the runner."
      - name: List files in the repository
        run: |
          ls ${{ github.workspace }}
      - run: echo "🍏 This job's status is ${{ job.status }}."
```


https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions

https://github.com/cypress-io/github-action/blob/master/.github/workflows/example-basic.yml

https://github.com/marketplace/actions/yaml-update-action

https://github.com/aws-actions/amazon-ecr-login

https://github.com/marketplace/actions/docker-login


### AWS Public Elastic Container Registry (ECR)
```yaml
name: ci

on:
  push:
    branches: main

jobs:
  login:
    runs-on: ubuntu-latest
    steps:
      -
        name: Login to Public ECR
        uses: docker/login-action@v2
        with:
          registry: public.ecr.aws
          username: ${{ secrets.AWS_ACCESS_KEY_ID }}
          password: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        env:
          AWS_REGION: <region>
```

### GitLab
```yaml
name: ci

on:
  push:
    branches: main

jobs:
  login:
    runs-on: ubuntu-latest
    steps:
      -
        name: Login to GitLab
        uses: docker/login-action@v2
        with:
          registry: registry.gitlab.com
          username: ${{ secrets.GITLAB_USERNAME }}
          password: ${{ secrets.GITLAB_PASSWORD }}
```

### GitHub Container Registry
```yaml
name: ci

on:
  push:
    branches: main

jobs:
  login:
    runs-on: ubuntu-latest
    steps:
      -
        name: Login to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
```

### Docker Hub
```yaml
name: ci

on:
  push:
    branches: main

jobs:
  login:
    runs-on: ubuntu-latest
    steps:
      -
        name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
```


```yaml
### Reusable workflow to plan terraform deployment, create artifact and upload to workflow artifacts for consumption ###
name: "Build_TF_Plan"
on:
  workflow_call:
    inputs:
      path:
        description: 'Specifies the path of the root terraform module.'
        required: true
        type: string
      tf_version:
        description: 'Specifies version of Terraform to use. e.g: 1.1.0 Default=latest.'
        required: false
        type: string
        default: latest
      gh_environment:
        description: 'Specifies the GitHub deployment environment.'
        required: false
        type: string
        default: null
      tf_vars_file:
        description: 'Specifies the Terraform TFVARS file.'
        required: true
        type: string
    secrets:
      cli_config_credentials_token:
        description: 'cli config credentials token'
        required: true

jobs:
  build-plan:
    runs-on: ubuntu-latest
    environment: ${{ inputs.gh_environment }}
    defaults:
      run:
        shell: bash
        working-directory: ${{ inputs.path }}
        
    steps:
      - name: Checkout
        uses: actions/checkout@v3.1.0
        
      - name: Change file name
        run: | 
          mv ${{ github.workspace }}/${{ inputs.path }}/${{ inputs.gh_environment }}.tfvars  ${{ github.workspace }}/${{ inputs.path }}/${{ inputs.gh_environment }}.auto.tfvars 
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2.0.2
        with:
          terraform_version: ${{ inputs.tf_version }}
          cli_config_credentials_token: ${{ secrets.cli_config_credentials_token }}

      - name: Terraform Init
        id: init
        run: terraform init
      
      - name: Terraform Validate
        id: validate
        run: terraform validate

      - name: Terraform Plan
        id: plan
        run: terraform plan
        continue-on-error: true

      - name: Terraform Plan Status
        if: steps.plan.outcome == 'failure'
        run: exit 1



### Reusable workflow to download terraform artifact built by `az_tf_plan` and apply the artifact/plan ###
name: "Apply_TF_Plan"
on:
  workflow_call:
    inputs:
      path:
        description: 'Specifies the path of the root terraform module.'
        required: true
        type: string
      tf_version:
        description: 'Specifies version of Terraform to use. e.g: 1.1.0 Default=latest.'
        required: false
        type: string
        default: latest
      gh_environment:
        description: 'Specifies the GitHub deployment environment.'
        required: false
        type: string
        default: null
      tf_vars_file:
        description: 'Specifies the Terraform TFVARS file.'
        required: true
        type: string
    secrets:
      cli_config_credentials_token:
        description: 'cli config credentials token'
        required: true

jobs:
  apply-plan:
    runs-on: ubuntu-latest
    environment: ${{ inputs.gh_environment }}
    defaults:
      run:
        shell: bash
        working-directory: ${{ inputs.path }}
    steps:
      - name: Checkout
        uses: actions/checkout@v3.1.0
        
      - name: Change file name
        run: | 
          mv ${{ github.workspace }}/${{ inputs.path }}/${{ inputs.gh_environment }}.tfvars  ${{ github.workspace }}/${{ inputs.path }}/${{ inputs.gh_environment }}.auto.tfvars 
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2.0.2
        with:
          terraform_version: ${{ inputs.tf_version }}
          cli_config_credentials_token: ${{ secrets.cli_config_credentials_token }}

      - name: Terraform Init
        id: init
        run: terraform init
      
      - name: Terraform Validate
        id: validate
        run: terraform validate

      - name: Terraform Plan
        id: plan
        run: terraform plan
        continue-on-error: true

      - name: Terraform Plan Status
        if: steps.plan.outcome == 'failure'
        run: exit 1

      - name: Terraform Apply
        run: terraform apply -auto-approve


on:
  push:
    branches: [ main ]
  workflow_dispatch:
    branches: [ main ]

name: mdh-app

jobs:
  deploy:
    name: Deploy
    runs-on: ubuntu-latest

    steps:
    - name: Checkout
      uses: actions/checkout@v2

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.ACCESS_KEY }}
        aws-secret-access-key: ${{ secrets.SECRET_KEY }}
        aws-region: us-west-2

    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1

    - name: Build, tag, and push the image to Amazon ECR
      id: build-image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: ${{ secrets.REPO_NAME }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        # Build a docker container and push it to ECR 
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        echo "Pushing image to ECR..."
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        echo "name=image::$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT
```


```yaml
name: Build and Deploy Docker Compose App to AWS ECS

on:
  push:
    branches: [ main ]

env:
  AWS_REGION: us-east-1
  ECS_CLUSTER: my-ecs-cluster
  SERVICE_NAME: my-ecs-service
  IMAGE_NAME: my-docker-image
  TAG: latest
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ env.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ env.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Install Docker and Docker Compose
        run: |
          sudo apt-get update
          sudo apt-get install -y docker.io docker-compose

      - name: Build and tag Docker image
        run: |
          docker-compose build $IMAGE_NAME
          docker tag $IMAGE_NAME $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE_NAME:$TAG

      - name: Push Docker image to Amazon ECR
        run: |
          aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
          docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE_NAME:$TAG

      - name: Deploy Docker Compose app to ECS
        run: |
          ecs-cli configure --region $AWS_REGION --cluster $ECS_CLUSTER
          ecs-cli compose --project-name $SERVICE_NAME service up
```