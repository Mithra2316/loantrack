\# LoanTrack — Three-Tier DevOps \& SRE Assessment



A containerized three-tier loan tracking application built with \*\*Nginx\*\* (frontend), \*\*Flask\*\* (backend API), and \*\*PostgreSQL 16\*\* (database), deployed locally via Docker Compose and Kubernetes (Minikube).



\## Tool Versions

\- \*\*Docker Engine\*\*: 29.6.1 (Docker Desktop)

\- \*\*Docker Compose\*\*: v5.2.0

\- \*\*minikube\*\*: v1.39.0

\- \*\*kubectl\*\*: v1.36.1

\- \*\*Container Runtime\*\*: `containerd` (Minikube) / Docker Engine 29.6.1 (Compose)



\## Architecture



```text

Browser / Client

&#x20;  │

&#x20;  ├── Docker Compose (:8080) ──► Nginx Frontend (:8080)

&#x20;  │                                    │

&#x20;  └── Kubernetes (NodePort 30080) ────►│ HTTP /api/\*

&#x20;                                       ▼

&#x20;                              Flask Backend (:5000, ClusterIP, 3 replicas)

&#x20;                                       │

&#x20;                                       ├── GET /healthz (process alive)

&#x20;                                       ├── GET /readyz  (DB reachable)

&#x20;                                       │

&#x20;                                       ▼ psycopg2 ThreadedConnectionPool

&#x20;                              PostgreSQL 16 (:5432, ClusterIP, PVC / Named Volume)

```



\- \*\*Frontend → Backend\*\*: Nginx serves the UI and proxies `/api/\*` requests to the Flask backend over HTTP; the frontend never connects directly to the database.

\- \*\*Backend → Database\*\*: Flask connects to PostgreSQL on port `5432` using a connection pool and exponential backoff retry on startup.



\## Run Instructions



\### 1. Docker Compose

1\. Clone the repository and create your local `.env` file from the example:

&#x20;  ```powershell

&#x20;  Copy-Item .env.example .env

&#x20;  ```

2\. Build and start all three tiers in detached mode:

&#x20;  ```powershell

&#x20;  docker compose up -d --build

&#x20;  ```

3\. Verify running containers and open the app at `http://localhost:8080`:

&#x20;  ```powershell

&#x20;  docker compose ps

&#x20;  ```

4\. Stop containers (data persists on the named volume) or stop and remove volumes (clears DB data):

&#x20;  ```powershell

&#x20;  docker compose down

&#x20;  docker compose down -v

&#x20;  ```



\### 2. Kubernetes (Minikube)

1\. Ensure Minikube is running:

&#x20;  ```powershell

&#x20;  minikube start

&#x20;  ```

2\. Create the real Kubernetes Secret from `k8s/secret.example.yaml` (never commit real credentials):

&#x20;  ```powershell

&#x20;  Copy-Item k8s/secret.example.yaml k8s/secret.yaml

&#x20;  # Edit k8s/secret.yaml with your base64-encoded DB credentials, then apply:

&#x20;  kubectl apply -f k8s/namespace.yaml

&#x20;  kubectl apply -f k8s/secret.yaml

&#x20;  ```

3\. Run the idempotent one-command deployment script (builds/loads images into Minikube, applies manifests in order, waits for rollouts, and prints the URL):

&#x20;  ```powershell

&#x20;  ./scripts/deploy.sh

&#x20;  ```

4\. Open the frontend service URL in your browser:

&#x20;  ```powershell

&#x20;  minikube service frontend -n loantrack --url

&#x20;  ```



\## Design Decisions

\- \*\*Backend base image choice\*\*: `python:3.12-slim` keeps the final image small (< 300 MB) while maintaining full compatibility with `psycopg2` and Python dependencies.

\- \*\*Layer-cache boundary\*\*: Copying and installing `requirements.txt` before copying application source code ensures Docker reuses cached dependency layers whenever only source code changes.

\- \*\*StatefulSet vs. Deployment for Postgres\*\*: A `Deployment` with a `PersistentVolumeClaim` was used for straightforward single-instance local Minikube persistence, whereas a `StatefulSet` with `volumeClaimTemplate` is preferred in production for stable network identities and per-pod storage.

\- \*\*Liveness vs. readiness\*\*: Liveness (`/healthz`) checks whether the process is alive so Kubernetes can restart wedged containers, while readiness (`/readyz`) checks database connectivity so traffic only routes to pods ready to serve queries.

\- \*\*Memory limit vs. CPU limit\*\*: Exceeding a container's memory limit causes the kernel to terminate it (`OOMKilled`), whereas exceeding its CPU limit throttles CPU time without killing the container.

\- \*\*Base64 in Secrets vs. production encryption\*\*: Base64 is reversible encoding rather than encryption; in production, Kubernetes Secrets should be protected with KMS encryption at rest alongside an external secret manager (such as AWS Secrets Manager or HashiCorp Vault via External Secrets Operator).



\## Additional Documentation

\- \[BRANCHING.md](BRANCHING.md) — Git branching model and team workflow recommendation

\- \[EVIDENCE.md](EVIDENCE.md) — Verification commands, outputs, UI screenshots, and issues faced

\- \[AI\_USAGE.md](AI\_USAGE.md) — AI assistance log and review notes

