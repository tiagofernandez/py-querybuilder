ifeq (, $(shell which python3))
    $(error "No python3 on PATH.")
endif

define HELP

Usage:
    make help                  show available commands

    make clean                 remove generated files
    make setup                 create the virtualenv
    make install               install dependencies

    make shell                 start a python shell
    make test                  run unit tests
    make coverage              run test coverage checks
    make lint                  run lint inspections
    make format                format the source code

    make build                 build & package the library
    make publish               release to pypi.org
endef

export HELP

.PHONY: docs venv

help:
	@echo "$$HELP"

venv:
ifeq (, $(VIRTUAL_ENV))
	$(error "Virtualenv not activated.")
endif

clean:
	rm -rf .egg *.egg-info build dist
	find . -type d -name ".pytest_cache" -exec rm -rf "{}" +;
	find . -type d -name "__pycache__" -exec rm -rf "{}" +;

setup: clean
	pip install --upgrade virtualenv
	virtualenv -p python3 venv

install: venv
	pip install -r requirements.txt
	pre-commit install

shell: venv
	ipython

test: venv
	python -m pytest --capture=no

coverage: venv
	python -m pytest --cov=py_querybuilder

lint: venv
	flake8 py_querybuilder tests

format: venv
	black py_querybuilder tests

docs: venv
	rm -rf docs
	cd sphinx && make html
	touch docs/.nojekyll

build: clean test lint
	python setup.py bdist_wheel

build-zip: build
	python setup.py sdist --formats=gztar,zip

publish: build
	twine upload dist/*
