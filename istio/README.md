## Enable Istio in a Namespace
```
kubectl label namespace <namespace> istio-injection=enabled
kubectl label namespace app istio-injection=enabled
```

## [Install with Helm](https://istio.io/latest/docs/setup/install/helm/)

```
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update
kubectl create namespace istio-system
helm install istio-base manifests/charts/base -n istio-system
helm install istio-base istio/base -n istio-system
helm install istiod istio/istiod -n istio-system --wait
kubectl create namespace istio-ingress
kubectl label namespace istio-ingress istio-injection=enabled
helm install istio-ingress istio/gateway -n istio-ingress --wait
```

## AWS Load Balancer Controller
https://github.com/kubernetes-sigs/aws-load-balancer-controller/tree/main/helm/aws-load-balancer-controller
```
helm repo add eks https://aws.github.io/eks-charts
helm upgrade -i aws-load-balancer-controller eks/aws-load-balancer-controller -n kube-system --set clusterName=<k8s-cluster-name>
```

aws eks update-kubeconfig --name eks --region us-east-1

## Install choco
```
Set-ExecutionPolicy Bypass -Scope Process -Force; `
  iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
```

## install kubens
```
choco install kubens
```