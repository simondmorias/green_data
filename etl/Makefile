.PHONY: help venv install clean test deploy validate sync run-local format lint

help:
	@echo "Available commands:"
	@echo "  make venv       - Create virtual environment"
	@echo "  make install    - Install dependencies"
	@echo "  make clean      - Clean up generated files"
	@echo "  make test       - Run tests"
	@echo "  make deploy     - Deploy bundle to Databricks"
	@echo "  make validate   - Validate bundle configuration"
	@echo "  make sync       - Sync bundle to workspace"
	@echo "  make run-local  - Run job locally with Databricks Connect"
	@echo "  make format     - Format code with black"
	@echo "  make lint       - Run linting"

venv:
	python3 -m venv venv
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

install: venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	./venv/bin/databricks configure --profile rgm_poc

clean:
	rm -rf venv
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf dist
	rm -rf *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test:
	./venv/bin/pytest tests/ -v

validate:
	databricks bundle validate --profile rgm_poc

deploy:
	databricks bundle deploy --profile rgm_poc

sync:
	databricks bundle sync --profile rgm_poc --watch

run-local:
	./venv/bin/python -m src.jobs.sample_job

format:
	./venv/bin/black src/ tests/

lint:
	./venv/bin/black --check src/ tests/