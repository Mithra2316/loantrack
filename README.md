# LoanTrack - Three-Tier DevOps & SRE Assessment

A containerized three-tier loan tracking application built with Nginx (frontend), Flask (backend API), and PostgreSQL 16 (database), deployed locally via Docker Compose and Kubernetes (Minikube).

## Architecture
- Browser -> Nginx Frontend (:8080 / NodePort 30080)
- Nginx Frontend -> Flask Backend (/api/* -> ClusterIP :5000, 3 replicas, /healthz and /readyz)
- Flask Backend -> PostgreSQL 16 (ThreadedConnectionPool -> ClusterIP :5432, PVC, ConfigMap migrations)

## Key Highlights
- Multi-stage non-root Docker builds: loantrack-backend (196MB, user appuser) and loantrack-frontend (73.7MB, user nginx on port 8080).
- Backend connection pooling, exponential backoff DB retry on startup, /healthz liveness, /readyz readiness, and X-Pod-Name header.
- Kubernetes hardening in the loantrack namespace with ConfigMap, Secret, PVC, probes, resource requests/limits, rolling updates, and scripts/deploy.sh.

## Quick Start

### Docker Compose
docker compose up -d --build
docker compose down
docker compose down -v

### Kubernetes (Minikube)
./scripts/deploy.sh
minikube service frontend -n loantrack --url

## Documentation
- BRANCHING.md
- EVIDENCE.md
- AI_USAGE.md
