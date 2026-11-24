# AI Usage Log

| Task | Tool | What I Accepted As-Is | What I Changed and Why |
| --- | --- | --- | --- |
| Multi-stage Dockerfiles & Compose | Gemini | Base multi-stage build layout and Compose service wiring | Verified pinned tags, non-root users (`appuser`, `nginx`), `.dockerignore`, healthchecks, and backend image size (< 300 MB) locally |
| Kubernetes manifests & `scripts/deploy.sh` | Gemini | Initial YAML structure for Deployments, Services, ConfigMap, Secret, and PVC | Adapted image loading to `minikube image load` for Windows `containerd`, scoped everything to `loantrack`, and tuned probe timings |
| Troubleshooting & verification commands | Gemini | Diagnostic flow (`kubectl describe`, `logs`, `get events`, rollout/scaling checks) | Adjusted Linux shell commands to Windows PowerShell syntax and re-ran against live pods after fixing a stale branch image |
| Documentation (`README.md`, `EVIDENCE.md`) | Gemini | Section structure and checklist alignment | Replaced placeholder versions with exact local tool versions and recorded my real terminal outputs, IPs, and issues faced |

## Where AI Was Wrong or Misleading
AI initially suggested `minikube docker-env` for building images directly inside Minikube, which failed on my Windows setup using the `containerd` runtime; I caught this immediately from the terminal error and switched to building locally with `minikube image load`. It also occasionally generated Linux-style shell commands or multi-line PowerShell snippets that broke formatting when pasted, which I noticed by inspecting `git diff` and the rendered Markdown on GitHub before merging.s