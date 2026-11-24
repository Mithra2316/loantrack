# Git Branching and Pull Request Workflow

This repository uses a GitFlow-style branching model:

- main: Production-ready, stable releases only. Updated exclusively via Pull Requests from develop.
- develop: Integration branch where completed features are merged and verified before release.
- feature/*: Short-lived branches created from develop for isolated units of work:
  - feature/backend-docker-upgrades: Connection pooling, startup retry with exponential backoff, /healthz and /readyz probes, multi-stage non-root Dockerfiles, .dockerignore, and Compose networking.
  - feature/k8s-hardening: Dedicated loantrack namespace, ConfigMap, resource requests and limits, liveness and readiness probes, and scripts/deploy.sh.
  - feature/docs: README.md, BRANCHING.md, EVIDENCE.md, AI_USAGE.md, and UI screenshots.

## Workflow Rules
1. Create every feature branch from an up-to-date develop branch.
2. Keep commits small, focused, and easy to review.
3. Merge changes into develop and main via GitHub Pull Requests with a clear summary and review comments.
