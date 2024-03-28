#!make

help:
	@echo ""
	@echo "Usage:"
	@echo ""
	@echo "Setup, build and run (Docker):"
	@echo "  make docker-start                                              Start the scraper and database docker containers"
	@echo "  make docker-stop                                               Stop the scraper and database docker containers"
	@echo "  make docker-build                                              Build the docker containers"
	@echo "  make docker-start-db                                           Start a database instance on a docker container"
	@echo "  make docker-stop-db                                            Stop the database docker container"
	@echo ""
	@echo "Setup:"
	@echo "  make setup-dev                                         		Setup the project including development dependencies"
	@echo "  make setup-dev-arm64                                         	Setup the project including development dependencies for arm64 architecture"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint-fix                                                  Run the linter with autofix flag activated"
	@echo "  make test                                                      Run the server tests"
	@echo "  make coverage-test                                             Run the server tests with code coverage"
	@echo ""

# Default variables
COMPOSE ?= docker-compose
DETACH = "-d"

# Docker

docker-start:
	$(COMPOSE) up $(DETACH)

docker-stop:
	$(COMPOSE) stop

docker-build:
	$(COMPOSE) up $(DETACH) --build

# Requirements

setup-dev:
	pip install -r ./config/requirements.txt --no-cache

setup-dev-arm64:
	arch -arm64 pip install -r ./config/requirements.txt --no-cache

## Database

docker-start-db:
	$(COMPOSE) up $(DETACH) db

docker-stop-db:
	$(COMPOSE) stop db

## Code lint and format

lint-fix:
	black .

default: help
