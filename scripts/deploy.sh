#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="loantrack"

echo "==> Checking Minikube status..."
if ! minikube status >/dev/null 2>&1; then
  minikube start
fi

echo "==> Building images locally and loading into Minikube..."
docker build -t loantrack-backend:v1 ./backend
docker build -t loantrack-frontend:v1 ./frontend
minikube image load loantrack-backend:v1
minikube image load loantrack-frontend:v1

echo "==> Applying namespace..."
kubectl apply -f k8s/namespace.yaml

echo "==> Applying Secret..."
if [ -f k8s/secret.yaml ]; then
  kubectl apply -f k8s/secret.yaml
else
  echo "WARNING: k8s/secret.yaml not found; applying k8s/secret.example.yaml for local demo."
  kubectl apply -f k8s/secret.example.yaml
fi

echo "==> Applying ConfigMaps..."
kubectl apply -f k8s/configmap.yaml
kubectl create configmap db-migrations \
  --from-file=db/migrations \
  -n "$NAMESPACE" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "==> Deploying PostgreSQL, Backend, and Frontend..."
kubectl apply -f k8s/db.yaml
kubectl rollout status deployment/db -n "$NAMESPACE" --timeout=120s

kubectl apply -f k8s/backend.yaml
kubectl rollout status deployment/backend -n "$NAMESPACE" --timeout=120s

kubectl apply -f k8s/frontend.yaml
kubectl rollout status deployment/frontend -n "$NAMESPACE" --timeout=120s

echo "==> Deployment complete! Access URL:"
minikube service frontend -n "$NAMESPACE" --url