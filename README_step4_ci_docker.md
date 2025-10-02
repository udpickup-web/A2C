# Step 4 — CI: build & push Docker image (Docker Hub + GHCR)

This workflow builds a multi-arch image and pushes to GHCR by default and to Docker Hub if secrets are set.

## Files
- `.github/workflows/docker-publish.yml`
- `.dockerignore`

## Setup
1. Repo Settings → Actions → General → set **Read and write permissions**.
2. Add secrets (optional) for Docker Hub:
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_TOKEN`  (Docker Hub → Account Settings → Security → New Access Token)

GHCR uses the built-in `GITHUB_TOKEN`.

## Images
- GHCR: `ghcr.io/<owner>/analog2cad-core:<tags>`
- Docker Hub (optional): `docker.io/<DOCKERHUB_USERNAME>/analog2cad-core:<tags>`

## Tags
- `latest` on pushes to `main`
- `sha-<FULL_SHA>` for each commit
- `<git tag>` when you push a tag (`v1.2.3`, `release-...`)

## Local test
```bash
docker build -t analog2cad-core:dev .
docker run --rm -p 8011:8011 analog2cad-core:dev
```
