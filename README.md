# LoanTrack - Three-Tier DevOps & SRE Assessment

A containerized three-tier loan tracking application built with Nginx (frontend), Flask (backend API), and PostgreSQL 16 (database), deployed locally via Docker Compose and Kubernetes (Minikube).

develop
## Tool Versions
- Docker: Docker Engine and Docker Compose v2
- Kubernetes CLI: kubectl
- Local Cluster: minikube
- Container Runtime: containerd (Minikube) / Docker Engine (Compose)

## Architecture
- Browser -> Nginx Frontend (:8080 / NodePort 30080)
- Nginx Frontend -> Flask Backend (/api/* -> ClusterIP :5000, 3 replicas, /healthz and /readyz)
- Flask Backend -> PostgreSQL 16 (ThreadedConnectionPool -> ClusterIP :5432, PVC, migrations)

## Key Highlights
- Multi-stage non-root Docker builds: loantrack-backend (196MB, user appuser) and loantrack-frontend (73.7MB, user nginx on port 8080), with .dockerignore and backend HEALTHCHECK.
- Versioned SQL migrations and seed data, connection pooling, exponential backoff DB retry on startup, /healthz liveness, /readyz readiness, and X-Pod-Name header.
- Kubernetes hardening in the loantrack namespace with ConfigMap, Secret (secret.example.yaml), PVC, probes, resource requests/limits, rolling updates/rollback, and scripts/deploy.sh.

## Architecture
- Browser -> Nginx Frontend (:8080 / NodePort 30080)
- Nginx Frontend -> Flask Backend (/api/* -> ClusterIP :5000, 3 replicas, /healthz and /readyz)
- Flask Backend -> PostgreSQL 16 (ThreadedConnectionPool -> ClusterIP :5432, PVC, ConfigMap migrations)

## Key Highlights
- Multi-stage non-root Docker builds: loantrack-backend (196MB, user appuser) and loantrack-frontend (73.7MB, user nginx on port 8080).
- Backend connection pooling, exponential backoff DB retry on startup, /healthz liveness, /readyz readiness, and X-Pod-Name header.
- Kubernetes hardening in the loantrack namespace with ConfigMap, Secret, PVC, probes, resource requests/limits, rolling updates, and scripts/deploy.sh.
 main

## Quick Start

### Docker Compose
 develop
Copy-Item .env.example .env
main
docker compose up -d --build
docker compose down
docker compose down -v

### Kubernetes (Minikube)
./scripts/deploy.sh
minikube service frontend -n loantrack --url

 develop
## Design Decisions
- Backend base image choice: python:3.12-slim keeps the runtime compact while supporting PostgreSQL client dependencies.
- Layer-cache boundary: Installing dependencies before copying application code reuses cached layers on code changes.
- StatefulSet vs. Deployment for Postgres: A Deployment with a PVC (or StatefulSet with volumeClaimTemplate) keeps DB data outside container restarts; a Deployment + PVC was used here for single-instance local Minikube setup.
- Liveness vs. readiness: /healthz checks if the process is alive for restarts, while /readyz checks DB reachability so traffic only goes to ready pods.
- Memory limit vs. CPU limit: Exceeding the memory limit causes OOMKilled termination, while exceeding the CPU limit causes CPU throttling.
- Secret base64 vs. production encryption: Base64 is encoding rather than encryption; production should use KMS encryption at rest and an external secret manager.


 main
## Documentation
- BRANCHING.md
- EVIDENCE.md
- AI_USAGE.md
