## Install jfrog-artifactory in AWS EC2
- An AWS T2.small EC2 instance (Linux)
- Open port 8081 and 8082 in the security group
- https://jfrog.com/community/open-source/
- https://jfrog.bintray.com/artifactory/
- https://www.youtube.com/watch?v=eB6CDSR8VCA
- https://github.com/ravdy/DevOps/blob/master/Artifactory/Setup_Artifactory.md

```sh
yum update
yum install java-1.8* -y 
yum update

cd /opt
wget https://jfrog.bintray.com/artifactory/jfrog-artifactory-oss-6.9.6.zip
unzip jfrog-artifactory-oss-6.9.6.zip
cd artifactory-oss-6.9.6
cd bin/
./artifactory.sh start

#access artifactory from browser
http://<PUBLIC_IP_Address>:8081 

# Provide credentials
username: admin
password: passwrod 
````

## Upload
```sh
curl -u<USERNAME>:<PASSWORD> -T <PATH_TO_FILE> "http://3.85.244.75:8081/artifactory/pecs-helm/<TARGET_FILE_PATH>"
curl -uadmin:password -T jfrog-artifactory-oss-6.9.6.zip "http://3.85.244.75:8081/artifactory/pecs-helm/artifact/jfrog-artifactory-oss-6.9.6.zip"

curl -uadmin:AP99yLDG59fv7wwUTo1JoJ4DzmC -T <PATH_TO_FILE> "http://3.85.244.75:8081/artifactory/pecs-helm/<TARGET_FILE_PATH>"
```

## Download
```sh
curl -u<USERNAME>:<PASSWORD> -O "http://3.85.244.75:8081/artifactory/pecs-helm/<TARGET_FILE_PATH>"
curl -uadmin:password -O "http://3.85.244.75:8081/artifactory/pecs-helm/test.pem"

curl -uadmin:AP99yLDG59fv7wwUTo1JoJ4DzmC -O "http://3.85.244.75:8081/artifactory/pecs-helm/<TARGET_FILE_PATH>"
```

## install jfrog cli
```sh
cd /opt
curl -fL https://getcli.jfrog.io | sh
 export PATH=$PATH:/opt/
jfrog --version
```

## links
https://landing.jfrog.com/quick-purchase/pricing

https://devopseaylearning.jfrog.io/ui/login/

https://landing.jfrog.com/quick-purchase/pricing


## Upload charts from helm and helm-local
```sh
curl -utiajearad@gmail.com:cmVmdGtuOjAxOjE3MDg2OTkwMDg6ZzFIWHBrejRJaExFZnFmMmdUMllKeXRtbGtF -T <PATH_TO_FILE> "https://devopseaylearning.jfrog.io/artifactory/helm/<TARGET_FILE_PATH>"

helm repo add helm https://devopseaylearning.jfrog.io/artifactory/api/helm/helm --username tiajearad@gmail.com --password cmVmdGtuOjAxOjE3MDg2OTkwMDg6ZzFIWHBrejRJaExFZnFmMmdUMllKeXRtbGtF


curl -utiajearad@gmail.com:cmVmdGtuOjAxOjE3MDg2OTkwMDg6ZzFIWHBrejRJaExFZnFmMmdUMllKeXRtbGtF -T <PATH_TO_FILE> "https://devopseaylearning.jfrog.io/artifactory/helm-local/<TARGET_FILE_PATH>"

helm repo add helm-local https://devopseaylearning.jfrog.io/artifactory/api/helm/helm-local --username tiajearad@gmail.com --password cmVmdGtuOjAxOjE3MDg2OTkwMDg6ZzFIWHBrejRJaExFZnFmMmdUMllKeXRtbGtF
```

## Adding from your own repository
1. Download a `index.yaml` from either helm and helm-local 
2. Upload it in your own repository
3. add the repository
```
helm repo add pecs-helm https://devopseaylearning.jfrog.io/artifactory/api/helm/pecs-helm --username tiajearad@gmail.com --password cmVmdGtuOjAxOjE3MDg3MDAyMzA6MERWUjROcWJIeVJNTUl4eFd6aUNOWnlzOFhh
```

## Create struucture to store charts
The folder cluster-autoscaler and jenkins will be create automatically if it does not exist inside pecs-helm in repository
```
curl -utiajearad@gmail.com:cmVmdGtuOjAxOjE3MDg3MDA5NDc6Nzl2UDlCYVJDRm9wMTJwZFFXQzdvQjlLM2xy -T helm-test-chart-0.1.0.tgz "https://devopseaylearning.jfrog.io/artifactory/pecs-helm/cluster-autoscaler/helm-test-chart-0.1.0.tgz"

curl -utiajearad@gmail.com:cmVmdGtuOjAxOjE3MDg3MDA5NDc6Nzl2UDlCYVJDRm9wMTJwZFFXQzdvQjlLM2xy -T mychart-0.1.0.tgz "https://devopseaylearning.jfrog.io/artifactory/pecs-helm/jenkins/mychart-0.1.0.tgz"
```

## Pushing a Helm chart to AWS ECR
```sh
https://docs.aws.amazon.com/AmazonECR/latest/userguide/push-oci-artifact.html

helm create helm-test-chart
helm lint helm-test-chart
helm dependency update helm-test-chart
helm package helm-test-chart

 aws ecr create-repository \
      --repository-name helm-test-chart \
      --region us-east-1


aws ecr get-login-password \
     --region us-east-1 | helm registry login \
     --username AWS \
     --password-stdin 788210522308.dkr.ecr.us-east-1.amazonaws.com

helm push helm-test-chart-0.1.0.tgz oci://788210522308.dkr.ecr.us-east-1.amazonaws.com/
```

## Using Amazon ECR Images with Amazon EKS
```sh
https://docs.aws.amazon.com/AmazonECR/latest/userguide/ECR_on_EKS.html#using-helm-charts-eks

aws ecr get-login-password \
     --region us-west-2 | helm registry login \
     --username AWS \
     --password-stdin aws_account_id.dkr.ecr.region.amazonaws.com

aws ecr get-login-password \
     --region us-east-1 | helm registry login \
     --username AWS \
     --password-stdin 788210522308.dkr.ecr.us-east-1.amazonaws.com

helm install ecr-chart-demo oci://aws_account_id.dkr.ecr.region.amazonaws.com/helm-test-chart --version 0.1.0
helm install ecr-chart-demo oci://788210522308.dkr.ecr.us-east-1.amazonaws.com/helm-test-chart --version 0.1.0

helm3 upgrade ${chartName} --install ../../charts/${chartName} --values ${chartName}.yaml --namespace ${chartName}"
```