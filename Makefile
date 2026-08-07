.PHONY: setup install demo load train dashboard test lint security check preflight all

PYTHON := .venv/bin/python
PIP := .venv/bin/pip

setup:
	python3 -m venv .venv
	$(PIP) install -r requirements-dev.txt

install:
	$(PIP) install -r requirements-dev.txt

demo:
	$(PYTHON) -m src.generate_demo --rows 12000

load:
	$(PYTHON) -m src.pipeline

train:
	$(PYTHON) -m src.model

dashboard:
	.venv/bin/streamlit run app/dashboard.py

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check .

security:
	$(PYTHON) -m bandit -q -r src app
	$(PYTHON) -m pip_audit -r requirements.txt

preflight:
	$(PYTHON) scripts/preflight.py

check: test lint security

all: demo load train check

