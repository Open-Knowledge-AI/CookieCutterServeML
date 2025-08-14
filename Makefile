#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME := serve-ml
PYTHON_INTERPRETER := python3
PACKAGE_FILE := pyproject.toml
VERSION_EXCLUDE_PATTERNS ?= *.md

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python Dependencies
.PHONY: requirements
requirements:
	$(PYTHON_INTERPRETER) -m pip install -U pip
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt


## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete


## Lint using flake8 and black (use `make format` to do formatting)
.PHONY: lint
lint:
	flake8 app
	black --check --config pyproject.toml app


## Format source code with black
.PHONY: format
format:
	black --config pyproject.toml app


.PHONY: dependencies
dependencies:
	@echo "Installing dependencies for the container..."
	$(PYTHON_INTERPRETER) -m pip install -U pip
	apt install -y python3-venv


## Set up python interpreter environment
.PHONY: create_environment
create_environment:
	@if command -v $(PYTHON_INTERPRETER) > /dev/null; then \
		if [ ! -d "venv" ]; then \
			$(PYTHON_INTERPRETER) -m venv venv; \
			echo "Virtual environment created."; \
		else \
			echo "Virtual environment already exists."; \
		fi; \
		source venv/bin/activate && $(MAKE) requirements; \
	else \
		echo "$(PYTHON_INTERPRETER) is not installed. Please install it first."; \
	fi


## Activate python environment
.PHONY: activate_environment
activate_environment:
	@if [ -d "venv" ]; then \
  		source venv/bin/activate; \
		echo "Virtual environment activated."; \
	else \
		echo "Virtual environment does not exist. Please run 'make create_environment' first."; \
	fi

.PHONY: setup_hooks
setup_hooks:
	@if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then \
		pre-commit install; \
		pre-commit autoupdate --repo https://github.com/pre-commit/pre-commit-hooks; \
		pre-commit install --hook-type pre-push; \
	else \
		echo "Not inside a Git repository. Skipping pre-commit setup."; \
	fi


.PHONY: env
env: create_environment activate_environment requirements setup_hooks

.PHONY: check-version
check-version:
	@bash -c '\
		set -e; \
		echo "📥 Fetching latest origin/main..."; \
		git fetch origin main >/dev/null 2>&1 || { echo "❌ Failed to fetch origin/main"; exit 1; }; \
		changed_files=$$(git diff --name-only origin/main...HEAD | grep -vE "$(shell echo $(VERSION_EXCLUDE_PATTERNS) | sed "s/ /|/g; s/\*/.*/g")" || true); \
		echo "🔍 Checking for changed files..."; \
		if [ -z "$$changed_files" ]; then \
			echo "$$changed_files"; \
			echo "ℹ️  Only excluded files changed ($(VERSION_EXCLUDE_PATTERNS)), skipping version check."; \
			exit 0; \
		fi; \
		echo "📄 Relevant changed files:"; \
		echo "$$changed_files" | sed "s/^/   - /"; \
		if echo "$$changed_files" | grep -q "^$(PACKAGE_FILE)$$"; then \
			echo "ℹ️  $(PACKAGE_FILE) already changed — assuming version bump done, skipping check."; \
			exit 0; \
		fi; \
		# Check if we are pushing to main \
		echo "🔍 Code changes detected without version bump — checking..."; \
		main_version=$$(git show origin/main:$(PACKAGE_FILE) | python3 -c '\''import sys, importlib.util; spec = importlib.util.find_spec("tomllib") or importlib.util.find_spec("tomli"); mod = importlib.import_module("tomllib" if spec.name=="tomllib" else "tomli"); data = mod.load(sys.stdin.buffer); print(data["project"]["version"])'\''); \
		current_version=$$(python3 -c '\''import sys, importlib.util; spec = importlib.util.find_spec("tomllib") or importlib.util.find_spec("tomli"); mod = importlib.import_module("tomllib" if spec.name=="tomllib" else "tomli"); data = mod.load(open("$(PACKAGE_FILE)", "rb")); print(data["project"]["version"])'\''); \
		if [ "$$main_version" = "$$current_version" ]; then \
			echo "❌ Version has NOT changed! (still $$current_version)"; \
			exit 1; \
		else \
			echo "✅ Version changed: $$main_version → $$current_version"; \
		fi; \
	'


.PHONY: run
run:
	@echo "Running the application..."
	cd app && \
	$(PYTHON_INTERPRETER) -m uvicorn main:app --host 0.0.0.0 --port 8000

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
