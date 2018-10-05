SHELL := /bin/bash

help:
	@echo "Usage:"
	@echo " make release | Release to pypi."
	@echo " make test | Run the tests."

release:
	python setup.py sdist bdist_wheel
	twine upload dist/*

test:
	@coverage run ./tests/run.py
	@coverage report
	@flake8 .
