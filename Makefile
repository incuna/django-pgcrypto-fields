SHELL := /bin/bash

help:
	@echo "Usage:"
	@echo " make release | Release to pypi."
	@echo " make test | Run the tests."

release:
	rm -r -f dist/*
	rm -r -f build/*
	python setup.py sdist bdist_wheel
	twine upload dist/*

test:
	rm -r -f dist/*
	rm -r -f build/*
	@coverage run ./tests/run.py
	@coverage report
	@flake8 .
