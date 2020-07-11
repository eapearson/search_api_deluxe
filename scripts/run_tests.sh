#!/bin/sh

set -e

export PYTHONPATH=.
export WORKSPACE_URL="http://localhost:5555/ws"

path=${1:-"tests/unit"}

poetry run flake8
poetry run mypy --ignore-missing-imports src/**/*.py
poetry run bandit -r src
poetry run pytest -vv -s --cov=./src --cov-report=xml $path
poetry run coverage html
poetry run coverage report
