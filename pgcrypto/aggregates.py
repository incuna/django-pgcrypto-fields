from django.conf import settings
from django.db.models import Aggregate


class PGPPublicKeySQL:
    """Custom SQL aggregate to decrypt a field with public key.

    `PGPPublicKeySQL` provides a SQL template using pgcrypto to decrypt
    data from a field in the database.

    `function` defines `pgp_pub_decrypt` which is a pgcrypto SQL function.
    This function takes two arguments:
    - a encrypted message (bytea);
    - a key (bytea).

    `%(function)s` in `template` is populated by `sql_function`.

    `%(field)s` is replaced with the field's name.

    `dearmor` is used to unwrap the key from the PGP key.
    """
    function = 'pgp_pub_decrypt'
    template = "%(function)s(%(field)s, dearmor('{}'))".format(
        settings.PRIVATE_PGP_KEY,
    )


class PGPSymmetricKeySQL:
    """Custom SQL aggregate to decrypt a field with public key.

    `PGPSymmetricKeySQL` provides a SQL template using pgcrypto to decrypt
    data from a field in the database.

    `function` defines `pgp_sym_decrypt` which is a pgcrypto SQL function.
    This function takes two arguments:
    - a encrypted message (bytea);
    - a key (bytea).

    `%(function)s` in `template` is populated by `sql_function`.

    `%(field)s` is replaced with the field's name.
    """
    function = 'pgp_sym_decrypt'
    template = "%(function)s(%(field)s, '{}')".format(
        settings.PGCRYPTO_KEY,
    )


class EncryptionBase(Aggregate):
    """Base class to add a custom aggregate method to a query."""

    def add_to_query(self, query, alias, col, source, is_summary):
        """Add the aggregate to the query.

        `alias` is `{self.lookup}__decrypt` where 'decrypt' is `self.name.lower()`.

        `self.lookup` is defined in `models.Aggregate.__init__`.
        """
        aggregate = self.sql(
            col,
            source=source,
            is_summary=is_summary,
            **self.extra
        )
        query.aggregates[alias] = aggregate


class PGPPublicKeyAggregate(PGPPublicKeySQL, EncryptionBase):
    """PGP public key based aggregation.

    `pgp_pub_encrypt` and `dearmor` are pgcrypto functions which encrypt
    the field's value with the PGP key unwrapped by `dearmor`.
    """
    name = 'decrypted'


class PGPSymmetricKeyAggregate(PGPSymmetricKeySQL, EncryptionBase):
    """PGP symmetric key based aggregation.

    `pgp_sym_encrypt` is a pgcrypto functions, encrypts the field's value
    with a key.
    """
    name = 'decrypted'
