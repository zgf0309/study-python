SHELL := /bin/zsh
PYTHON := /opt/homebrew/bin/python3
VENV_PYTHON := .venv/bin/python
VENV_PIP := $(VENV_PYTHON) -m pip
PORT ?= 8090

.PHONY: install init-venv stop run run-debug health

init-venv:
	if [[ ! -x $(VENV_PYTHON) || ! -f .venv/pyvenv.cfg ]]; then \
		rm -rf .venv; \
		$(PYTHON) -m venv .venv; \
	elif ! $(VENV_PYTHON) -m pip --version >/dev/null 2>&1; then \
		rm -rf .venv; \
		$(PYTHON) -m venv .venv; \
	fi

install: init-venv
	$(VENV_PIP) install -r requirements.txt

stop:
	pids=$$(lsof -ti tcp:$(PORT)); \
	if [[ -n "$$pids" ]]; then \
		printf '%s\n' "$$pids" | xargs kill; \
	fi

run: install stop
	$(VENV_PYTHON) -m uvicorn --app-dir $(CURDIR) app.main:app --host 127.0.0.1 --port $(PORT)

run-debug: install stop
	$(VENV_PYTHON) -m uvicorn --app-dir $(CURDIR) app.main:app --reload --host 127.0.0.1 --port $(PORT)

health:
	curl -s http://127.0.0.1:$(PORT)/api/health