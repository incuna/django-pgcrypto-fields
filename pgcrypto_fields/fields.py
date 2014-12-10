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
    descriptor_class = EncryptedProxyField

    def contribute_to_class(self, cls, name, **kwargs):
        """
        Add a decrypted field proxy to the model.

        Add to the field model an `EncryptedProxyField` to get the decrypted
        values of the field.

        The decrypted value can be accessed using the field's name attribute on
        the model instance.
        """
        super().contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, self.descriptor_class(field=self))


class TextFieldHash(models.TextField):
    """Keyed hash TextField.

    `TextFieldHash` uses 'pgcrypto' to encrypt data in a postgres database.
    """
    def get_placeholder(self, value=None, connection=None):
        """
        Tell postgres to encrypt this field with a hashing function.

        The `value` string is checked to determine if we need to hash or keep
        the current value.

        `connection` is ignored here as we don't need custom operators.
        """
        if value.startswith('\\x'):
            return '%s'
        return self.encrypt_sql


class TextFieldPGP(PGPDecryptMixin, models.TextField):
    """Encrypted TextField.

    `TextFieldPGP` uses 'pgcrypto' to encrypt data in a postgres database.
    """
    def db_type(self, connection=None):
        """Value stored in the database is hexadecimal."""
        return 'bytea'

    def get_placeholder(self, value=None, connection=None):
        """
        Tell postgres to encrypt this field using PGP.

        `value` and `connection` are ignored here as we don't need custom operators.
        """
        return self.encrypt_sql


class DigestField(TextFieldHash):
    """Digest field for postgres."""
    encrypt_sql = DIGEST_SQL
DigestField.register_lookup(DigestLookup)


class HMACField(TextFieldHash):
    """HMAC field for postgres."""
    encrypt_sql = HMAC_SQL
HMACField.register_lookup(HMACLookup)


class PGPPublicKeyField(TextFieldPGP):
    """PGP public key encrypted field for postgres."""
    encrypt_sql = PGP_PUB_ENCRYPT_SQL
    aggregate = PGPPublicKeyAggregate


class PGPSymmetricKeyField(TextFieldPGP):
    """PGP symmetric key encrypted field for postgres."""
    encrypt_sql = PGP_SYM_ENCRYPT_SQL
    aggregate = PGPSymmetricKeyAggregate
