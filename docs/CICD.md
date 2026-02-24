# CI/CD GitHub Actions (Docker Hub + Kubernetes)

## Workflow
Le pipeline est dans `.github/workflows/ci.yml`.

Sur `pull_request`:
- validation Python (lint, format, mypy, `manage.py check`, tests Django)

Sur `push` sur `main` (et `workflow_dispatch`):
- build Docker de `app/`
- push vers Docker Hub (`latest` + `${GITHUB_SHA}`)
- déploiement Kubernetes (`k8s/`), puis `kubectl set image` avec le tag `${GITHUB_SHA}`

## Secrets GitHub requis
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `KUBE_CONFIG_B64` (contenu du kubeconfig encodé en base64)
- `DJANGO_SECRET_KEY`

## Variables GitHub optionnelles
- `DOCKER_IMAGE_NAME` (ex: `monuser/ptw-web`)  
  Défaut: `${DOCKERHUB_USERNAME}/ptw-web`
- `DJANGO_ALLOWED_HOSTS` (ex: `app.example.com`)
- `DJANGO_DEBUG` (`0` recommandé)

## Manifests Kubernetes
- `k8s/namespace.yaml`
- `k8s/deployment.yaml`
- `k8s/service.yaml`

Namespace utilisé: `ptw`.

## Générer KUBE_CONFIG_B64 (PowerShell)
```powershell
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes((Get-Content .\votre-kubeconfig -Raw)))
```

## Notes sécurité
- Ne pas versionner de kubeconfig dans le dépôt.
- `.gitignore` ignore maintenant les fichiers `*kubeconfig*`.
