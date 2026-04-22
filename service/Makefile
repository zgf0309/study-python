SHELL := /bin/zsh
PYTHON := /opt/homebrew/bin/python3
VENV_PYTHON := .venv/bin/python
VENV_PIP := .venv/bin/pip
PORT ?= 8090

.PHONY: install init-venv run run-debug health

init-venv:
	if [[ ! -d .venv ]]; then $(PYTHON) -m venv .venv; fi

install: init-venv
	$(VENV_PIP) install -r requirements.txt

run: install
	$(VENV_PYTHON) -m uvicorn app.main:app --host 127.0.0.1 --port $(PORT)

run-debug: install
	$(VENV_PYTHON) -m uvicorn app.main:app --reload --host 127.0.0.1 --port $(PORT)

health:
	curl -s http://127.0.0.1:$(PORT)/api/health