#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = serve-ml
PYTHON_INTERPRETER = python3

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
	else \
		echo "Not inside a Git repository. Skipping pre-commit setup."; \
	fi


.PHONY: env
env: create_environment activate_environment requirements setup_hooks


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
