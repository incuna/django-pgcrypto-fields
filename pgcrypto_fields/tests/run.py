#! /usr/bin/env python
"""From http://stackoverflow.com/a/12260597/400691."""
import sys

from colour_runner.django_runner import ColourRunnerMixin
import dj_database_url
from django.conf import settings


settings.configure(
    DATABASES={
        'default': dj_database_url.config(
            default='postgres://localhost/pgcrypto_fields'
        ),
    },
    INSTALLED_APPS=(),
    MIDDLEWARE_CLASSES = (),
)

import django
if django.VERSION >= (1, 7):
    django.setup()

from django.test.runner import DiscoverRunner


class TestRunner(ColourRunnerMixin, DiscoverRunner):
    """Enable colorised output."""


test_runner = TestRunner(verbosity=1)
failures = test_runner.run_tests(['pgcrypto_fields'])
if failures:
    sys.exit(1)
