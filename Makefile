# Use double quotes for assignments
.ONESHELL:

# Calculate the environment prefix
ENV_PREFIX=$(shell python -c "if __import__('pathlib').Path('.venv/Scripts/pip.exe').exists(): print('.venv/Scripts/')")

.PHONY: help
help:             	## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@findstr "^##" Makefile | findstr /V findstr

.PHONY: venv
venv:			## Create a virtual environment
	@echo "Creating virtualenv ..."
	@if exist .venv rmdir /S /Q .venv
	@python -m venv .venv
	python -m pip install -U pip
	@echo.
	@echo "Run '.venv\\Scripts\\activate' to enable the environment"

.PHONY: install
install:		## Install dependencies
	python -m pip install -r requirements-dev.txt
	python -m pip install -r requirements-test.txt
	python -m pip install -r requirements.txt

STRESS_URL = https://aletelcom-latam-challenge-app.onrender.com
.PHONY: stress-test
stress-test:
	@if not exist reports mkdir reports
	python -m locust -f tests/stress/api_stress.py --print-stats --html reports/stress-test.html --run-time 60s --headless --users 100 --spawn-rate 1 -H $(STRESS_URL)

.PHONY: model-test
model-test:			## Run tests and coverage
	@if not exist reports mkdir reports
	python -m pytest --cov-config=.coveragerc --cov-report term --cov-report html:reports/html --cov-report xml:reports/coverage.xml --junitxml=reports/junit.xml --cov=challenge tests/model

.PHONY: api-test
api-test:			## Run tests and coverage
	@if not exist reports mkdir reports
	python -m pytest --cov-config=.coveragerc --cov-report term --cov-report html:reports/html --cov-report xml:reports/coverage.xml --junitxml=reports/junit.xml --cov=challenge tests/api

.PHONY: build
build:			## Build locally the python artifact
	python -m setup.py bdist_wheel
