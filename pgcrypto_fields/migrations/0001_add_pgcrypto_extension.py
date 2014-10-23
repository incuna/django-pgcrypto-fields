from django.db import migrations


CREATE_EXTENSION = 'CREATE EXTENSION IF NOT EXISTS pgcrypto;'
DROP_EXTENSION = 'DROP EXTENSION pgcrypto;'


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.RunSQL(CREATE_EXTENSION, DROP_EXTENSION),
    ]
