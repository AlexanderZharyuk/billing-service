include .env

help:
	@echo "🪄  PREPARE ENVIRONMENT"
	@echo "---------------------------------------------------------------------"
	@echo "  init                Install all python requirements"
	@echo "  up                  Run docker composition for development"
	@echo "  down                Destroy docker composition"
	@echo ""
	@echo "⚙️  DEVELOPMENT"
	@echo "---------------------------------------------------------------------"
	@echo "  lint                Check python syntax & style by black and flake8"
	@echo "  lint-apply          Apply isort/black fixes linter (autoformat)"
	@echo "  sec                 Security linter (bandit)"
	@echo "  run                 Start application"

sec:
	@bandit -r src/

lint:
	@flake8 src
	@black src --check --diff

lint-apply:
	@isort src/*
	@black src/*

init:
	@pip install -r requirements-dev.txt

up:
	@docker compose up -d

down:
	@docker compose down -v

run:
	@uvicorn src.main:app --reload --port ${LISTEN_PORT}