.PHONY: help dev down test test-unit test-integration test-e2e lint format \
        build images chaos-test perf-test certs clean docs

PYTHON ?= python3
COMPOSE ?= docker compose

help:  ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "Targets:\n"} \
		/^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

dev: certs  ## Bring up the full local stack
	$(COMPOSE) up -d
	@echo ""
	@echo "Meridian is up:"
	@echo "  Grafana:      http://localhost:3000  (admin/admin)"
	@echo "  Prometheus:   http://localhost:9090"
	@echo "  Alertmanager: http://localhost:9093"
	@echo "  Controller:   https://localhost:8443"
	@echo "  Agent /metrics: http://localhost:9101/metrics"

down:  ## Tear down the local stack
	$(COMPOSE) down -v

certs:  ## Generate development PKI (CA + agent + controller + operator)
	bash scripts/generate-certs.sh

test: test-unit test-integration  ## Run unit + integration tests

test-unit:  ## Run unit tests for all services
	cd services/agent && $(PYTHON) -m pytest tests/unit -q
	cd services/controller && $(PYTHON) -m pytest tests/unit -q
	cd services/cli && $(PYTHON) -m pytest tests -q
	cd services/chaos && $(PYTHON) -m pytest tests -q

test-integration:  ## Run integration tests (requires docker)
	cd services/agent && $(PYTHON) -m pytest tests/integration -q
	cd services/controller && $(PYTHON) -m pytest tests/integration -q

test-e2e:  ## Run end-to-end tests against the full stack
	$(PYTHON) -m pytest tests/e2e -q

chaos-test:  ## Run nightly chaos suite
	$(PYTHON) -m pytest tests/chaos -q --tb=short

perf-test:  ## Run performance benchmarks
	$(PYTHON) benchmarks/agent_throughput.py
	$(PYTHON) benchmarks/controller_api_load.py
	$(PYTHON) scripts/check-slo-compliance.py

lint:  ## Lint everything
	ruff check services/ libs/ scripts/ tests/
	mypy services/ libs/
	yamllint -c .yamllint.yml config/ deploy/ .github/
	hadolint services/*/Dockerfile
	shellcheck scripts/*.sh

format:  ## Auto-format
	ruff check --fix services/ libs/ scripts/ tests/
	ruff format services/ libs/ scripts/ tests/

images:  ## Build all container images
	docker build -t meridian/agent:dev -f services/agent/Dockerfile .
	docker build -t meridian/controller:dev -f services/controller/Dockerfile .
	docker build -t meridian/cli:dev -f services/cli/Dockerfile .
	docker build -t meridian/chaos:dev -f services/chaos/Dockerfile .

build: images  ## Alias for images

docs:  ## Build documentation site
	bash tools/docs-build.sh

clean:  ## Clean caches and generated artifacts
	find . -name __pycache__ -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name .pytest_cache -type d -exec rm -rf {} +
	find . -name .ruff_cache -type d -exec rm -rf {} +
	find . -name .mypy_cache -type d -exec rm -rf {} +
