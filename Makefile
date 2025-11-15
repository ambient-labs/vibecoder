.PHONY: install run delete-all help % 

help:
	@echo "Available targets:"
	@echo "  make install  - Install package in editable mode"
	@echo "  make run       - Install and run vibecoder with arguments"
	@echo "  make run -- REPO [BRANCH] [MACHINE]  - Run with arguments"
	@echo "  Example: make run -- ambient-labs/vibecoder"
	@echo "  make delete-all  - Delete all active codespaces"

install_locally:
	@if [ ! -d .venv ]; then uv venv --python 3.11; fi
	uv pip install --python .venv/bin/python -e .

run: install_locally
	@uv run vibecoder $(filter-out $@ run --,$(MAKECMDGOALS))

delete-all: install_locally
	@uv run vibecoder --delete-all

%:
	@:

