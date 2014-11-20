from django.db import models

from pgcrypto_fields import (
    DIGEST_SQL,
    HMAC_SQL,
    PGP_PUB_ENCRYPT_SQL,
    PGP_SYM_ENCRYPT_SQL,
)
from pgcrypto_fields.aggregates import PGPPublicKeyAggregate, PGPSymmetricKeyAggregate
from pgcrypto_fields.lookups import DigestLookup, HMACLookup
from pgcrypto_fields.proxy import EncryptedProxyField


class PGPDecryptMixin:
    """Decrypt the field's value."""
    def contribute_to_class(self, cls, name, **kwargs):
        """
        Add a decrypted field proxy to the model.

        Add to the field model an `EncryptedProxyField` to get the decrypted
        values of the field.

        Decrypted value is accessible through `{field_name}_decrypted`.
        """
        super().contribute_to_class(cls, name, **kwargs)

        decrypted_name = '{}_decrypted'.format(self.name)
        setattr(cls, decrypted_name, EncryptedProxyField(field=self))


class TextFieldBase(models.TextField):
    """Encrypted TextField.

    `TextFieldBase` uses 'pgcrypto' to encrypt data in a postgres database.
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
DigestField.register_lookup(DigestLookup)


class HMACField(TextFieldBase):
    """HMAC field for postgres."""
    encrypt_sql = HMAC_SQL
HMACField.register_lookup(HMACLookup)


class PGPPublicKeyField(PGPDecryptMixin, TextFieldBase):
    """PGP public key encrypted field for postgres."""
    encrypt_sql = PGP_PUB_ENCRYPT_SQL
    aggregate = PGPPublicKeyAggregate


class PGPSymmetricKeyField(PGPDecryptMixin, TextFieldBase):
    """PGP symmetric key encrypted field for postgres."""
    encrypt_sql = PGP_SYM_ENCRYPT_SQL
    aggregate = PGPSymmetricKeyAggregate
