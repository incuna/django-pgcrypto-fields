from django.db import models

from pgcrypto import (
    DIGEST_SQL,
    HMAC_SQL,
    PGP_PUB_ENCRYPT_SQL_WITH_NULLIF,
    PGP_SYM_ENCRYPT_SQL_WITH_NULLIF,
)
from pgcrypto.lookups import (
    HashLookup,
)
from pgcrypto.mixins import (
    DecimalPGPFieldMixin,
    get_setting,
    HashMixin,
    PGPPublicKeyFieldMixin,
    PGPSymmetricKeyFieldMixin,
)


class TextDigestField(HashMixin, models.TextField):
    """Text digest field for postgres."""
    encrypt_sql = DIGEST_SQL

    def get_encrypt_sql(self, connection):
        """Get encrypt sql."""
        return self.encrypt_sql.format(get_setting(connection, 'PGCRYPTO_KEY'))


TextDigestField.register_lookup(HashLookup)


class TextHMACField(HashMixin, models.TextField):
    """Text HMAC field for postgres."""
    encrypt_sql = HMAC_SQL


TextHMACField.register_lookup(HashLookup)


class EmailPGPPublicKeyField(PGPPublicKeyFieldMixin, models.EmailField):
    """Email PGP public key encrypted field."""


class IntegerPGPPublicKeyField(PGPPublicKeyFieldMixin, models.IntegerField):
    """Integer PGP public key encrypted field."""
    encrypt_sql = PGP_PUB_ENCRYPT_SQL_WITH_NULLIF
    cast_type = 'INT4'


class TextPGPPublicKeyField(PGPPublicKeyFieldMixin, models.TextField):
    """Text PGP public key encrypted field."""


class CharPGPPublicKeyField(PGPPublicKeyFieldMixin, models.CharField):
    """Char PGP public key encrypted field."""


class DatePGPPublicKeyField(PGPPublicKeyFieldMixin, models.DateField):
    """Date PGP public key encrypted field for postgres."""
    encrypt_sql = PGP_PUB_ENCRYPT_SQL_WITH_NULLIF
    cast_type = 'DATE'


class DateTimePGPPublicKeyField(PGPPublicKeyFieldMixin, models.DateTimeField):
    """DateTime PGP public key encrypted field for postgres."""
    encrypt_sql = PGP_PUB_ENCRYPT_SQL_WITH_NULLIF
    cast_type = 'TIMESTAMP'


class EmailPGPSymmetricKeyField(PGPSymmetricKeyFieldMixin, models.EmailField):
    """Email PGP symmetric key encrypted field."""


class IntegerPGPSymmetricKeyField(PGPSymmetricKeyFieldMixin, models.IntegerField):
    """Integer PGP symmetric key encrypted field."""
    encrypt_sql = PGP_SYM_ENCRYPT_SQL_WITH_NULLIF
    cast_type = 'INT4'


class TextPGPSymmetricKeyField(PGPSymmetricKeyFieldMixin, models.TextField):
    """Text PGP symmetric key encrypted field for postgres."""


class CharPGPSymmetricKeyField(PGPSymmetricKeyFieldMixin, models.CharField):
    """Char PGP symmetric key encrypted field for postgres."""


class DatePGPSymmetricKeyField(PGPSymmetricKeyFieldMixin, models.DateField):
    """Date PGP symmetric key encrypted field for postgres."""
    encrypt_sql = PGP_SYM_ENCRYPT_SQL_WITH_NULLIF
    cast_type = 'DATE'


class DateTimePGPSymmetricKeyField(PGPSymmetricKeyFieldMixin, models.DateTimeField):
    """DateTime PGP symmetric key encrypted field for postgres."""
    encrypt_sql = PGP_SYM_ENCRYPT_SQL_WITH_NULLIF
    cast_type = 'TIMESTAMP'


class DecimalPGPPublicKeyField(DecimalPGPFieldMixin,
                               PGPPublicKeyFieldMixin, models.DecimalField):
    """Decimal PGP public key encrypted field for postgres."""


class DecimalPGPSymmetricKeyField(DecimalPGPFieldMixin,
                                  PGPSymmetricKeyFieldMixin, models.DecimalField):
    """Decimal PGP symmetric key encrypted field for postgres."""


class FloatPGPPublicKeyField(PGPPublicKeyFieldMixin, models.FloatField):
    """Float PGP public key encrypted field for postgres."""
    encrypt_sql = PGP_PUB_ENCRYPT_SQL_WITH_NULLIF
    cast_type = 'DOUBLE PRECISION'


class FloatPGPSymmetricKeyField(PGPSymmetricKeyFieldMixin, models.FloatField):
    """Float PGP symmetric key encrypted field for postgres."""
    encrypt_sql = PGP_SYM_ENCRYPT_SQL_WITH_NULLIF
    cast_type = 'DOUBLE PRECISION'


class TimePGPPublicKeyField(PGPPublicKeyFieldMixin, models.TimeField):
    """Time PGP public key encrypted field for postgres."""
    encrypt_sql = PGP_PUB_ENCRYPT_SQL_WITH_NULLIF
    cast_type = 'TIME'


class TimePGPSymmetricKeyField(PGPSymmetricKeyFieldMixin, models.TimeField):
    """Float PGP symmetric key encrypted field for postgres."""
    encrypt_sql = PGP_SYM_ENCRYPT_SQL_WITH_NULLIF
    cast_type = 'TIME'
