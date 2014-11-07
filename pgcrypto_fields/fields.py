from django.conf import settings
from django.db import models

from pgcrypto_fields.aggregates import PGPPublicKeyAggregate, PGPSymmetricKeyAggregate
from pgcrypto_fields.proxy import EncryptedProxyField


DIGEST_SQL = "digest(%s, 'sha512')"
HMAC_SQL = "hmac(%s, '{}', 'sha512')".format(settings.PGCRYPTO_KEY)

PGP_PUB_ENCRYPT_SQL = "pgp_pub_encrypt(%s, dearmor('{}'))".format(
    settings.PUBLIC_PGP_KEY,
)
PGP_SYM_ENCRYPT_SQL = "pgp_sym_encrypt(%s, '{}')".format(settings.PGCRYPTO_KEY)


class PGPDecryptMixin:
    """Sets two attributes on the fields."""
    def contribute_to_class(self, cls, name, **kwargs):
        """
        Add two fields on the model.

        Add to the field model an `EncryptedProxyField` to get the raw and
        decrypted values of the field.

        Raw value is accessible through `{field_name}_raw`.
        Decrypted value is accessible the usual way.
        """
        super().contribute_to_class(cls, name, **kwargs)

        raw_name = '{}_raw'.format(self.name)
        setattr(cls, self.name, EncryptedProxyField(field=self, raw=False))
        setattr(cls, raw_name, EncryptedProxyField(field=self))


class TextFieldBase(models.TextField):
    """Encrypted TextField.

    `TextFieldBase` deals with postgres and use pgcrypto to encode
    data to the database.
    """
    def db_type(self, connection=None):
        """Value stored in the database is hexadecimal."""
        return 'bytea'

    def get_placeholder(self, value=None, connection=None):
        """
        Tell postgres to encrypt this field with our public pgp key.

        `value` and `connection` are ignored here as we don't need other custom
        operator depending on the value.
        """
        return self.encrypt_sql


class DigestField(TextFieldBase):
    """Digest field for postgres."""
    encrypt_sql = DIGEST_SQL


class HMACField(TextFieldBase):
    """HMAC field for postgres."""
    encrypt_sql = HMAC_SQL


class PGPPublicKeyField(PGPDecryptMixin, TextFieldBase):
    """PGP public key based field for postgres."""
    encrypt_sql = PGP_PUB_ENCRYPT_SQL
    aggregate = PGPPublicKeyAggregate


class PGPSymmetricKeyField(PGPDecryptMixin, TextFieldBase):
    """PGP symmetric key based field for postgres."""
    encrypt_sql = PGP_SYM_ENCRYPT_SQL
    aggregate = PGPSymmetricKeyAggregate
