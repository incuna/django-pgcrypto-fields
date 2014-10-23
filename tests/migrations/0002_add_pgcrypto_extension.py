# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


CREATE_EXTENSION = 'CREATE EXTENSION pgcrypto;'
DROP_EXTENSION = 'DROP EXTENSION pgcrypto;'


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(CREATE_EXTENSION, DROP_EXTENSION),
    ]
