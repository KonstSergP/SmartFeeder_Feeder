
VENV := ../my_env
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
COVERAGE := $(VENV)/bin/coverage


.PHONY: all install run coverage clean deepclean
all: install coverage


install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install pytest coverage


run:
	$(PYTHON) main.py


coverage:
	$(COVERAGE) run --rcfile=settings/.coveragerc -m pytest
	$(COVERAGE) report


clean:
	@rm -rf __pycache__
	@rm -rf */__pycache__
	@rm -rf */*/__pycache__
	@rm -rf */*/*/__pycache__
	@rm -rf .pytest_cache
	@rm -rf .coverage
	@rm -f *.pyc
	@rm -f */*.pyc
	@rm -f */*/*.pyc
	@rm -f */*/*/*.pyc
	@rm -f *.log
	@rm -f api-error.log


deepclean: clean
	@rm -rf $(VENV)
