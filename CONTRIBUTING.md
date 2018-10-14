# Contributing to Django-PGCrypto-Fields

We welcome contributions in many forms:

* Code patches and enhancements
* Documentation improvements
* Bug reports and patch reviews

## Running Tests

Install the developers packages:

* `pip install -r requirements.txt --upgrade`
* Setup a local PostgreSQL server
* Create a PostreSQL database named `pgcrypto_fields`
* In your virtual env, run `make test`

## Releasing to PyPI

This section only applies to maintainers.

* `make release`
