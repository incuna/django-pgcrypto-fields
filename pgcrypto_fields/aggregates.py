from django.conf import settings
from django.db import models


class DecryptFunctionSQL(models.sql.aggregates.Aggregate):
    """Decrypt function SQL.

    `DecryptFunctionSQL` defines a template to render the SQL for decrypting
    a a field's value.

    It defines the `function` that implements the aggregate and the private key
    unwrapped by the `dearmor` function.

    `field` would receive the lookup name value.
    """
    sql_function = 'pgp_pub_decrypt'
    sql_template = "%(function)s(%(field)s, dearmor('{}'))".format(
        settings.PRIVATE_PGP_KEY,
    )


class Decrypt(models.Aggregate):
    """Decrypt aggregate.

    `Decrypt` setup an alias which would be populated following the template
    defined in `DecryptFunctionSQL`.
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
