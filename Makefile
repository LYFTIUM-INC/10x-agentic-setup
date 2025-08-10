SHELL := /usr/bin/bash

.PHONY: build up down ps logs lint audit ci

build:
	cd mcp_servers && docker build -t ml-enhanced-mcps-base:latest -f docker/Dockerfile.base . && docker compose build

up:
	cd mcp_servers && docker compose up -d

down:
	cd mcp_servers && docker compose down -v

ps:
	cd mcp_servers && docker compose ps

logs:
	cd mcp_servers && docker compose logs -f --no-color

lint:
	ruff check mcp_servers/shared/src || true
	autopep8 --version >/dev/null 2>&1 || true
	shellcheck --version >/dev/null 2>&1 || true

eval:
	@echo "Run: /eval:agent_bench_10x --suite quick"

audit:
	pip-audit -r mcp_servers/requirements.txt || true

ci:
	gh workflow run CI || true