# Verification Evidence and Troubleshooting Log

## 1. Docker Builds, Non-Root Users, and Live API (Part B)
- Image sizes: loantrack-backend:latest (196MB, under 300MB limit) and loantrack-frontend:latest (73.7MB).
- Non-root users verified: appuser in backend container and nginx in frontend container.
- Live API and DB check: GET /api/loans returned HTTP 200 with X-Pod-Name header, and PostgreSQL contained 6 rows (5 seeded plus 1 added row).

## 2. Health Probes, Startup Backoff, and Persistence (Part C)
- Stopped DB test: /healthz returned 200 while /readyz returned 503 with DB connection error.
- Startup retry with exponential backoff: Backend logged retry warnings (1s, 2s backoff) and initialized the connection pool on attempt 3.
- Volume persistence: docker compose down followed by docker compose up -d retained all 6 rows; docker compose down -v wiped and re-seeded back to 5 rows.

## 3. Kubernetes Deployment and Operational Tests (Part D)
- Live UI on Minikube (127.0.0.1:54330): Screenshot saved at docs/screenshots/k8s-ui.png.
- DNS resolution inside loantrack namespace: db resolved to 10.110.224.245 and backend resolved to 10.106.133.34.
- Scaled backend to 3 replicas and verified X-Pod-Name rotated across all three backend pods.
- Performed rolling update to loantrack-backend:v2 and rolled back cleanly via kubectl rollout undo.
- Deleted a backend pod and the db pod: both self-healed automatically and SELECT count(*) FROM loans returned 6 rows.

## 4. Real Issues Faced and Fixes
1. ErrImageNeverPull on loantrack-backend:v1: Image was built on host Docker rather than loaded into Minikube; fixed using minikube image load.
2. minikube docker-env failed on Windows with containerd runtime: Switched workflow and scripts/deploy.sh to build locally and use minikube image load.
3. Backend liveness/readiness probes returned 404 and restarted pods: feature/k8s-hardening was branched before feature/backend-docker-upgrades was merged, so :v1 lacked /healthz and /readyz; merged feature/backend-docker-upgrades, removed stale image with minikube image rm, rebuilt and reloaded :v1, and restarted the deployment.
