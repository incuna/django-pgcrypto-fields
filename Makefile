SHELL := /bin/bash

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

release: clean
	python setup.py sdist bdist_wheel
	twine upload dist/*

test: clean
	@coverage run ./tests/run.py
	@coverage report
	@flake8 .
