from pgcrypto_fields.aggregates import (
    PGPPublicKeyAggregate,
    PGPSymmetricKeyAggregate,
)
from pgcrypto_fields.proxy import EncryptedProxyField


class HashMixin:
    """Keyed hash mixin.

    `HashMixin` uses 'pgcrypto' to encrypt data in a postgres database.
    """
    def get_placeholder(self, value=None, connection=None):
        """
        Tell postgres to encrypt this field with a hashing function.

        The `value` string is checked to determine if we need to hash or keep
        the current value.

        `connection` is ignored here as we don't need custom operators.
        """
        if value is None or value.startswith('\\x'):
            return '%s'
        return self.encrypt_sql


class PGPMixin:
    """PGP encryption for field's value.

    `PGPMixin` uses 'pgcrypto' to encrypt data in a postgres database.
    """
    descriptor_class = EncryptedProxyField

    def __init__(self, *args, **kwargs):
        """`max_length` should be set to None as encrypted text size is variable."""
        kwargs['max_length'] = None
        super().__init__(*args, **kwargs)

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

    def db_type(self, connection=None):
        """Value stored in the database is hexadecimal."""
        return 'bytea'

    def get_placeholder(self, value=None, connection=None):
        """
        Tell postgres to encrypt this field using PGP.

        `value` and `connection` are ignored here as we don't need custom operators.
        """
        return self.encrypt_sql

    def _check_max_length_attribute(self, **kwargs):
        """Override `_check_max_length_attribute` to remove check on max_length."""
        return []


class PGPPublicKeyFieldMixin(PGPMixin):
    """PGP public key encrypted field mixin for postgres."""
    aggregate = PGPPublicKeyAggregate


class PGPSymmetricKeyFieldMixin(PGPMixin):
    """PGP symmetric key encrypted field mixin for postgred."""
    aggregate = PGPSymmetricKeyAggregate
