# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pgcrypto_fields.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EncryptedTextFieldModel',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('encrypted_value', pgcrypto_fields.fields.EncryptedTextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
