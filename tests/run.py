#! /usr/bin/env python
"""From http://stackoverflow.com/a/12260597/400691."""
import os
import sys

import dj_database_url
import django
from colour_runner.django_runner import ColourRunnerMixin
from django.conf import settings
from django.test.runner import DiscoverRunner


BASEDIR = os.path.dirname(os.path.dirname(__file__))
PUBLIC_PGP_KEY_PATH = os.path.abspath(os.path.join(BASEDIR, 'tests/keys/public.key'))
PRIVATE_PGP_KEY_PATH = os.path.abspath(os.path.join(BASEDIR, 'tests/keys/private.key'))


settings.configure(
    DATABASES={
        'default': dj_database_url.config(
            default='postgres://localhost/pgcrypto_fields'
        ),
    },
    INSTALLED_APPS=(
        'pgcrypto_fields',
        'tests',
    ),
    MIDDLEWARE_CLASSES=(),
    PUBLIC_PGP_KEY=open(PUBLIC_PGP_KEY_PATH, 'r').read(),
    PRIVATE_PGP_KEY=open(PRIVATE_PGP_KEY_PATH, 'r').read(),
    PGCRYPTO_KEY='ultrasecret',
)


if django.VERSION >= (1, 7):
    django.setup()


class TestRunner(ColourRunnerMixin, DiscoverRunner):
    """Enable colorised output."""


test_runner = TestRunner(verbosity=1)
failures = test_runner.run_tests(['tests'])
if failures:
    sys.exit(1)
