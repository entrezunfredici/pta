SHELL := /bin/sh

.PHONY: help ci-setup lint format format-check typecheck test build docker-up docker-down

help:
	@echo "Targets: help, ci-setup, lint, format, format-check, typecheck, test, build, docker-up, docker-down"

{% if stack_preset == "django" %}
ci-setup:
{% if python_tooling == "pip" %}
	@test -f app/requirements.txt || (echo "app/requirements.txt missing" && exit 1)
	@python -m pip install -r app/requirements.txt
	@if [ -f app/requirements-dev.txt ]; then python -m pip install -r app/requirements-dev.txt; fi
{% elif python_tooling == "poetry" %}
	@test -f app/pyproject.toml || (echo "app/pyproject.toml missing" && exit 1)
	@cd app && poetry install --no-interaction --no-root
{% elif python_tooling == "uv" %}
	@test -f app/requirements.txt || (echo "app/requirements.txt missing" && exit 1)
	@uv pip install -r app/requirements.txt
	@if [ -f app/requirements-dev.txt ]; then uv pip install -r app/requirements-dev.txt; fi
{% endif %}

lint:
	@cd app && ruff check .

format:
	@cd app && ruff format .

format-check:
	@cd app && ruff format --check .

typecheck:
	@cd app && mypy .

test:
	@cd app && pytest -q

build:
	@cd app && python -m build
{% elif stack_preset == "express-vue" %}
ci-setup:
{% if node_package_manager == "npm" %}
	@cd api && if [ -f package-lock.json ]; then npm ci; else npm install; fi
	@cd frontend && if [ -f package-lock.json ]; then npm ci; else npm install; fi
{% elif node_package_manager == "pnpm" %}
	@cd api && pnpm install --frozen-lockfile
	@cd frontend && pnpm install --frozen-lockfile
{% elif node_package_manager == "yarn" %}
	@cd api && yarn install --frozen-lockfile
	@cd frontend && yarn install --frozen-lockfile
{% endif %}

lint:
{% if node_package_manager == "npm" %}
	@cd api && npm run lint
	@cd frontend && npm run lint
{% elif node_package_manager == "pnpm" %}
	@cd api && pnpm run lint
	@cd frontend && pnpm run lint
{% elif node_package_manager == "yarn" %}
	@cd api && yarn run lint
	@cd frontend && yarn run lint
{% endif %}

format:
{% if node_package_manager == "npm" %}
	@cd api && npm run format
	@cd frontend && npm run format
{% elif node_package_manager == "pnpm" %}
	@cd api && pnpm run format
	@cd frontend && pnpm run format
{% elif node_package_manager == "yarn" %}
	@cd api && yarn run format
	@cd frontend && yarn run format
{% endif %}

format-check:
{% if node_package_manager == "npm" %}
	@cd api && npm run format:check
	@cd frontend && npm run format:check
{% elif node_package_manager == "pnpm" %}
	@cd api && pnpm run format:check
	@cd frontend && pnpm run format:check
{% elif node_package_manager == "yarn" %}
	@cd api && yarn run format:check
	@cd frontend && yarn run format:check
{% endif %}

typecheck:
{% if node_package_manager == "npm" %}
	@cd api && npm run typecheck
	@cd frontend && npm run typecheck
{% elif node_package_manager == "pnpm" %}
	@cd api && pnpm run typecheck
	@cd frontend && pnpm run typecheck
{% elif node_package_manager == "yarn" %}
	@cd api && yarn run typecheck
	@cd frontend && yarn run typecheck
{% endif %}

test:
{% if node_package_manager == "npm" %}
	@cd api && npm test
	@cd frontend && npm test
{% elif node_package_manager == "pnpm" %}
	@cd api && pnpm test
	@cd frontend && pnpm test
{% elif node_package_manager == "yarn" %}
	@cd api && yarn test
	@cd frontend && yarn test
{% endif %}

build:
{% if node_package_manager == "npm" %}
	@cd api && npm run build
	@cd frontend && npm run build
{% elif node_package_manager == "pnpm" %}
	@cd api && pnpm run build
	@cd frontend && pnpm run build
{% elif node_package_manager == "yarn" %}
	@cd api && yarn run build
	@cd frontend && yarn run build
{% endif %}
{% else %}
ci-setup:
	@echo "ci-setup placeholder" && exit 0

lint:
	@echo "lint placeholder" && exit 0

format:
	@echo "format placeholder" && exit 0

format-check:
	@echo "format-check placeholder" && exit 0

typecheck:
	@echo "typecheck placeholder" && exit 0

test:
	@echo "test placeholder" && exit 0

build:
	@echo "build placeholder" && exit 0
{% endif %}

{% if use_docker %}
docker-up:
	@docker compose up -d

docker-down:
	@docker compose down
{% else %}
docker-up:
	@echo "docker not enabled" && exit 0

docker-down:
	@echo "docker not enabled" && exit 0
{% endif %}
