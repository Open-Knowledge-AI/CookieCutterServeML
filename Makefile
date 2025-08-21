#################################################################################
# GLOBALS                                                                       #
#################################################################################

VENV_PATH := venv
PROJECT_NAME := serve-ml

PIP := $(VENV_PATH)/bin/pip
BLACK := $(VENV_PATH)/bin/black
FLAKE8 := $(VENV_PATH)/bin/flake8
UVICORN := $(VENV_PATH)/bin/uvicorn
PRE_COMMIT := $(VENV_PATH)/bin/pre-commit
PYTHON_INTERPRETER := $(VENV_PATH)/bin/python3

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies
.PHONY: requirements
requirements:
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt

## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8 and black (use `make format` to do formatting)
.PHONY: lint
lint:
	$(FLAKE8) app
	$(BLACK) --check --config pyproject.toml .

## Format source code with black
.PHONY: format
format:
	black --config pyproject.toml ./app/

.PHONY: dependencies
dependencies:
	@echo "Installing dependencies for the container..."
	$(PIP) install -U pip

## Set up python interpreter environment
.PHONY: create_environment
create_environment:
	@if command -v python3 > /dev/null; then \
		if [ ! -d "$(VENV_PATH)" ]; then \
			python3 -m venv $(VENV_PATH); \
			echo "Virtual environment created."; \
		else \
			echo "Virtual environment already exists."; \
		fi; \
		$(MAKE) requirements; \
	else \
		echo "python3 is not installed. Please install it first."; \
	fi

## Activate python environment
.PHONY: activate_environment
activate_environment:
	@if [ -d "$(VENV_PATH)" ]; then \
  		echo "Virtual environment activated."; \
	else \
		echo "Virtual environment does not exist. Please run 'make create_environment' first."; \
	fi

.PHONY: setup_hooks
setup_hooks:
	@if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then \
		$(PRE_COMMIT) install; \
		$(PRE_COMMIT) autoupdate --repo https://github.com/pre-commit/pre-commit-hooks; \
		$(PRE_COMMIT) install --hook-type pre-push; \
		$(PRE_COMMIT) install --hook-type pre-commit; \
		$(PRE_COMMIT) install --install-hooks; \
		echo "Pre-commit hooks set up successfully."; \
	else \
		echo "Not inside a Git repository. Skipping pre-commit setup."; \
	fi

.PHONY: env
env: create_environment activate_environment requirements setup_hooks

.PHONY: run
run:
	@echo "Running the application..."
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
