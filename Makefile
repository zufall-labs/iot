# Makefile
.PHONY: setup-hooks create-config
SHELL := /bin/bash

REPO_NAME ?= your-repo
GITHUB_ORG ?= zufall-labs

create-config:
	@echo "Make: Creating/updating .zflbs configuration..."
	@echo "GITHUB_ORG=$(GITHUB_ORG)" > .zflbs
	@echo "GITHUB_REPO=$(REPO_NAME)" >> .zflbs
	@echo "Make: Configuration file .zflbs created with repository name: $(REPO_NAME)"

setup-hooks: create-config
	@echo "Make: Running setup-hooks script..."
	@chmod -f +x ./qa/scripts/setup-hooks || true
	@QA_DIR=$$(pwd)/qa ./qa/scripts/setup-hooks
	@echo "Make: Setting up git hooks is finished"

show-config:
	@if [ -f .zflbs ]; then \
		echo "Make: Current configuration:"; \
		cat .zflbs; \
	else \
		echo "Make: No configuration file found."; \
	fi
