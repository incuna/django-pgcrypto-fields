.PHONY: clean-build lint help
.DEFAULT_GOAL := help

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
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

lint: ## Check style with flake8
	@flake8 . --exit-zero

clean-build: ## Remove build artifacts
	rm -r -f dist/*
	rm -r -f build/*
	rm -fr htmlcov/

build: clean-build ## Builds source and wheel package
	python setup.py sdist bdist_wheel
	ls -l dist

release: ## Package and upload a release
	twine upload dist/*

test: clean-build lint ## Run tests quickly with the default Python
	./tests/run.py

test-coverage: ## Check code coverage quickly with the default Python
	coverage run ./tests/run.py
	coverage report -m

test-coveralls: test-coverage ## Check code coverage with the default Python and Coveralls
	coveralls

test-coverage-html: test-coverage  ## Check code coverage quickly with the default Python and show report
	coverage html
	$(BROWSER) htmlcov/index.html
