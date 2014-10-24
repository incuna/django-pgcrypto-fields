from django.conf import settings
from django.db import models


class DecryptFunctionSQL(models.sql.aggregates.Aggregate):
    """Custom SQL aggregate to decrypt a field.

    `DecryptFunctionSQL` provides a SQL template using pgcrypto to decrypt
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


class Decrypt(models.Aggregate):
    """`Decrypt` creates an alias for `DecryptFunctionSQL`.

    `alias` is `{self.lookup}__decrypt` where 'decrypt' is `self.name.lower()`.

    `self.lookup` is defined in `models.Aggregate.__init__`.
    """
    name = 'Decrypt'

    def add_to_query(self, query, alias, col, source, is_summary):
        """Add the aggregate to the query."""
        aggregate = DecryptFunctionSQL(
            col,
            source=source,
            is_summary=is_summary,
            **self.extra
        )
        query.aggregates[alias] = aggregate
