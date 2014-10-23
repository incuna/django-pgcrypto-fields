#! /usr/bin/env python
"""From http://stackoverflow.com/a/12260597/400691."""
import sys

import dj_database_url
import django
from colour_runner.django_runner import ColourRunnerMixin
from django.conf import settings
from django.test.runner import DiscoverRunner


settings.configure(
    DATABASES={
        'default': dj_database_url.config(
            default='postgres://localhost/pgcrypto_fields'
        ),
    },
    INSTALLED_APPS=('tests',),
    MIDDLEWARE_CLASSES = (),
    PUBLIC_PGP_KEY='',
)


if django.VERSION >= (1, 7):
    django.setup()


class TestRunner(ColourRunnerMixin, DiscoverRunner):
    """Enable colorised output."""


test_runner = TestRunner(verbosity=1)
failures = test_runner.run_tests(['tests'])
if failures:
    sys.exit(1)
