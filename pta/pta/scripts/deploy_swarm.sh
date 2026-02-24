#!/usr/bin/env sh
set -eu

STACK_NAME=${STACK_NAME:-{{ project_slug }}}
DEPLOY_PATH=${DEPLOY_PATH:-/opt/{{ project_slug }}}
IMAGE_TAG=${IMAGE_TAG:-latest}

if [ ! -f "$DEPLOY_PATH/.env" ]; then
  echo "Missing .env in $DEPLOY_PATH"
  exit 1
fi

cd "$DEPLOY_PATH"

set -a
. ./.env
set +a

IMAGE_TAG="$IMAGE_TAG" docker stack deploy -c docker-compose.server.yml "$STACK_NAME"
