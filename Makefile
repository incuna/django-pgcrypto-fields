SHELL := /bin/bash

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@echo "Usage:"
	@echo " lint | Lint code with Flake8."
	@echo " make release | Release to PyPi."
	@echo " make test | Run the tests."

lint:
	@flake8 .

clean-build:
	rm -r -f dist/*
	rm -r -f build/*
	rm -fr htmlcov/

build: clean-build
	python setup.py sdist bdist_wheel

release: build
	twine upload dist/*

test: clean-build lint
	coverage run ./tests/run.py
	coverage report
	coverage html
	$(BROWSER) htmlcov/index.html
