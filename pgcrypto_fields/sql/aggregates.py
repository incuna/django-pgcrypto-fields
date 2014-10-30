from django.conf import settings
from django.db import models


class PGPPub(models.sql.aggregates.Aggregate):
    """Custom SQL aggregate to decrypt a field with public key.

    `PGPPub` provides a SQL template using pgcrypto to decrypt
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


class PGPSym(models.sql.aggregates.Aggregate):
    """Custom SQL aggregate to decrypt a field with public key.

    `PGPSym` provides a SQL template using pgcrypto to decrypt
    data from a field in the database.

    `sql_function` defines `pgp_sym_decrypt` which is a pgcrypto SQL function.
    This function takes two arguments:
    - a encrypted message (bytea);
    - a key (bytea).

    `%(function)s` in `sql_template` is populated by `sql_function`.

    `%(field)s` is replaced with the field's name.

    `dearmor` is used to unwrap the key from the PGP key.
    """
    sql_function = 'pgp_sym_decrypt'
    sql_template = "%(function)s(%(field)s, '{}')".format(
        settings.PGCRYPTO_KEY,
    )
