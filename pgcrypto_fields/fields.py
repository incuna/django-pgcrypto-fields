from django.conf import settings
from django.db import models


class EncryptedTextField(models.TextField):
    """Encrypted TextField.

    `EncryptedTextField` deals with postgres and use pgcrypto to encode
    data to the database. Compatible with django 1.6.x for migration.
    """
    def db_type(self, connection=None):
        """Value stored in the database is hexadecimal."""
        return 'bytea'

    def get_placeholder(self, value=None, connection=None):
        """
        Tell postgres to encrypt this field with our public pgp key.

        `%s` is replaced with the field's value.

        `value` and `connection` are ignored here as we don't need other custom
        operator depending on the value.

        `pgp_pub_encrypt` and `dearmor` are `pgcrypto` functions which encrypt
        the field's value with the PGP key unwrapped by `dearmor`.
        """
        return "pgp_pub_encrypt(%s, dearmor('{}'))".format(settings.PUBLIC_PGP_KEY)

    def south_field_triple(self):
        """Return a suitable description of this field for South."""
        from south.modelsinspector import introspector
        field_class = '{}.{}'.format(self.__class__.__module__, self.__class__.__name__)
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)
