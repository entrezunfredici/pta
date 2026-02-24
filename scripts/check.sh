#!/usr/bin/env sh
set -e

printf "Running checks...\n"

make ci-setup
make lint
make format-check
make typecheck
make test
