# How to test kubernetes setup locally


## Prerequisite

* Install Docker Docker

* Install minikube


## Using minikube


### Start minikube

```
minikube start
```

### Start minikube with logs

```
minikube start --driver=docker --alsologtostderr
```

### Show dashboard

```
minikube dashboard --url=false
```

### Clear local state

```
minikube delete
```

## Steps to test bibxml-indexer

### Go to bibxml-indexer source folder

```
cd ~/path/to/bibxml-indexer
```

### Start minikube and set docker environment

```
minikube start
eval $(minikube -p minikube docker-env)
```

### Show minikube dashboard

```
minikube dashboard --url=false
```


### Create redis, db, network, secret in another terminal

```
eval $(minikube -p minikube docker-env)
kubectl apply -f k8s/redis
kubectl apply -f k8s/db
kubectl apply -f k8s/network
kubectl apply -f k8s/secret
kubectl get po,svc,secret
```

### Build docker image locally

```
docker build -t bibxml/base .
```

### Apply db migration

```
kubectl apply -f k8s/job/db-migration.yaml
```

### Check migration is completed

```
kubectl get po
```

### Remove completed job

```
kubectl delete -f k8s/job/db-migration.yaml
```

### Create web, celery, flower

kubectl apply -f k8s/web
kubectl apply -f k8s/celery
kubectl apply -f k8s/flower

### Go to bibxml-service source folder

```
cd ~/path/to/bibxml-service
```

### Create bibxml-service

```
eval $(minikube -p minikube docker-env)
kubectl apply -f k8s/ws
kubectl get po,svc
```
