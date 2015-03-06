from django.conf import settings
from django.db import models
from django.db.models.sql.aggregates import Aggregate


class PGPPublicKeySQL(Aggregate):
    """Custom SQL aggregate to decrypt a field with public key.

    `PGPPublicKeySQL` provides a SQL template using pgcrypto to decrypt
    data from a field in the database.

    `sql_function` defines `pgp_pub_decrypt` which is a pgcrypto SQL function.
    This function takes two arguments:
    - a encrypted message (bytea);
    - a key (bytea).

    `%(function)s` in `sql_template` is populated by `sql_function`.

    `%(field)s` is replaced with the field's name.

    `dearmor` is used to unwrap the key from the PGP key.
    """
    sql_function = 'pgp_pub_decrypt'
    sql_template = "%(function)s(%(field)s, dearmor('{}'))".format(
        settings.PRIVATE_PGP_KEY,
    )


class PGPSymmetricKeySQL(Aggregate):
    """Custom SQL aggregate to decrypt a field with public key.

    `PGPSymmetricKeySQL` provides a SQL template using pgcrypto to decrypt
    data from a field in the database.

    `sql_function` defines `pgp_sym_decrypt` which is a pgcrypto SQL function.
    This function takes two arguments:
    - a encrypted message (bytea);
    - a key (bytea).

    `%(function)s` in `sql_template` is populated by `sql_function`.

    `%(field)s` is replaced with the field's name.
    """
    sql_function = 'pgp_sym_decrypt'
    sql_template = "%(function)s(%(field)s, '{}')".format(
        settings.PGCRYPTO_KEY,
    )


class EncryptionBase(models.Aggregate):
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


class PGPPublicKeyAggregate(EncryptionBase):
    """PGP public key based aggregation.

    `pgp_pub_encrypt` and `dearmor` are pgcrypto functions which encrypt
    the field's value with the PGP key unwrapped by `dearmor`.
    """
    name = 'decrypted'
    sql = PGPPublicKeySQL


class PGPSymmetricKeyAggregate(EncryptionBase):
    """PGP symmetric key based aggregation.

    `pgp_sym_encrypt` is a pgcrypto functions, encrypts the field's value
    with a key.
    """
    name = 'decrypted'
    sql = PGPSymmetricKeySQL
