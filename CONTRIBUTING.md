# Contributing to Django-PGCrypto-Fields

We welcome contributions in many forms:

* Code patches and enhancements
* Documentation improvements
* Bug reports and patch reviews

## Running Tests

* Install requirements to a virtual environment
* Setup a local PostgreSQL server
* Create a PostreSQL database named `pgcrypto_fields`
* In a terminal, run `make test`


## Releasing to PyPI

This section only applies to maintainers.

In your virtual environment, run

* `pip install pip --upgrade`
* `pip install setuptools wheel twine`
* `make release`