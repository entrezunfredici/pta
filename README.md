# {{ project_name }}

{% if project_description %}{{ project_description }}{% else %}Project description goes here.{% endif %}

## Getting Started

### Stack Preset
{% if stack_preset == "django" %}
- Preset: Django (Python)
- Tooling: {{ python_tooling }}
  - App entry: `app/manage.py`
  - Templates: `app/templates/`
  - Static: `app/static/`
{% elif stack_preset == "express-vue" %}
- Preset: Express + Vue (Node)
- Package manager: {{ node_package_manager }}
  - API: `api/`
  - Frontend: `frontend/`
{% else %}
- Preset: None (fill in your stack)
{% endif %}

### Environment
- A `.env` file is generated at project creation time based on your Copier answers.
- The JWT secret is generated locally during creation and never stored in the template.
- Domains for Traefik routing are stored in `.env` (update these for server deployments).

### Docker (optional)
{% if use_docker %}
Bring the stack up:

```bash
docker compose up -d
```

Bring the stack down:

```bash
docker compose down
```
{% else %}
Docker is not enabled for this project.
{% endif %}

### Deployment Mode
{% if deployment_mode == "local" %}
- Local mode includes a Traefik instance inside the project (HTTP on port 80, dashboard on 8080).
{% else %}
- Server mode excludes local Traefik. Use your global reverse proxy for HTTPS and routing.
{% endif %}

### Monitoring (optional)
{% if include_monitoring %}
- Grafana: `http://grafana.localhost`
- Prometheus: `http://prometheus.localhost`
{% else %}
Monitoring is not enabled for this project.
{% endif %}

### Swarm Deploy (CI)
This template supports automatic deploys on branch merges:
- `dev` -> preprod
- `main` -> prod

Required CI secrets:
- Docker Hub: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`
- SSH deploy: `DEPLOY_USER`, `DEPLOY_KEY`, `PREPROD_HOST`, `PROD_HOST`

Server requirements:
- The repo is present at `{{ deploy_path }}`
- `.env` is configured with real domains and secrets
- `docker stack deploy -c docker-compose.server.yml {{ deploy_stack_name }}` is allowed

### Linting, Formatting, Testing
- Commands are wired through the `Makefile` targets:
- `make ci-setup`, `make lint`, `make format-check`, `make typecheck`, `make test`, `make build`
- Use `scripts/check.sh` to run the full local CI-style checks.

## Project Updates (Copier)
This project was generated with Copier. To update with template changes:

```bash
copier update
```

## Windows Notes
- Prefer PowerShell scripts in `scripts/` on Windows.
- If using Bash on Windows, ensure LF line endings for `.sh` files.
