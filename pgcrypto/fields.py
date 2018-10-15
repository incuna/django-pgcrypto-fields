from django.db import models

from pgcrypto import (
    DIGEST_SQL,
    HMAC_SQL,
    INTEGER_PGP_PUB_ENCRYPT_SQL,
    INTEGER_PGP_SYM_ENCRYPT_SQL,
)
from pgcrypto.lookups import (
    DateTimeExactLookup,
    DateTimeGteLookup,
    DateTimeGtLookup,
    DateTimeLteLookup,
    DateTimeLtLookup,
    DateTimeRangeLookup,
    HashLookup,
)
from pgcrypto.mixins import (
    DatePGPPublicKeyFieldMixin,
    DatePGPSymmetricKeyFieldMixin,
    DateTimePGPPublicKeyFieldMixin,
    DateTimePGPSymmetricKeyFieldMixin,
    EmailPGPPublicKeyFieldMixin,
    EmailPGPSymmetricKeyFieldMixin,
    HashMixin,
    PGPPublicKeyFieldMixin,
    PGPSymmetricKeyFieldMixin,
)


class TextDigestField(HashMixin, models.TextField):
    """Text digest field for postgres."""
    encrypt_sql = DIGEST_SQL


TextDigestField.register_lookup(HashLookup)


class TextHMACField(HashMixin, models.TextField):
    """Text HMAC field for postgres."""
    encrypt_sql = HMAC_SQL


TextHMACField.register_lookup(HashLookup)


class EmailPGPPublicKeyField(EmailPGPPublicKeyFieldMixin, models.EmailField):
    """Email PGP public key encrypted field."""


class IntegerPGPPublicKeyField(PGPPublicKeyFieldMixin, models.IntegerField):
    """Integer PGP public key encrypted field."""
    encrypt_sql = INTEGER_PGP_PUB_ENCRYPT_SQL
    cast_type = 'INT4'


class TextPGPPublicKeyField(PGPPublicKeyFieldMixin, models.TextField):
    """Text PGP public key encrypted field."""


class DatePGPPublicKeyField(DatePGPPublicKeyFieldMixin, models.TextField):
    """Date PGP public key encrypted field for postgres."""


DatePGPPublicKeyField.register_lookup(DateTimeExactLookup)
DatePGPPublicKeyField.register_lookup(DateTimeLtLookup)
DatePGPPublicKeyField.register_lookup(DateTimeLteLookup)
DatePGPPublicKeyField.register_lookup(DateTimeGtLookup)
DatePGPPublicKeyField.register_lookup(DateTimeGteLookup)
DatePGPPublicKeyField.register_lookup(DateTimeRangeLookup)


class DateTimePGPPublicKeyField(DateTimePGPPublicKeyFieldMixin, models.TextField):
    """DateTime PGP public key encrypted field for postgres."""


DateTimePGPPublicKeyField.register_lookup(DateTimeExactLookup)
DateTimePGPPublicKeyField.register_lookup(DateTimeLtLookup)
DateTimePGPPublicKeyField.register_lookup(DateTimeLteLookup)
DateTimePGPPublicKeyField.register_lookup(DateTimeGtLookup)
DateTimePGPPublicKeyField.register_lookup(DateTimeGteLookup)
DateTimePGPPublicKeyField.register_lookup(DateTimeRangeLookup)


class EmailPGPSymmetricKeyField(EmailPGPSymmetricKeyFieldMixin, models.EmailField):
    """Email PGP symmetric key encrypted field."""


class IntegerPGPSymmetricKeyField(PGPSymmetricKeyFieldMixin, models.IntegerField):
    """Integer PGP symmetric key encrypted field."""
    encrypt_sql = INTEGER_PGP_SYM_ENCRYPT_SQL
    cast_type = 'INT4'


class TextPGPSymmetricKeyField(PGPSymmetricKeyFieldMixin, models.TextField):
    """Text PGP symmetric key encrypted field for postgres."""


class DatePGPSymmetricKeyField(DatePGPSymmetricKeyFieldMixin, models.TextField):
    """Date PGP symmetric key encrypted field for postgres."""


DatePGPSymmetricKeyField.register_lookup(DateTimeExactLookup)
DatePGPSymmetricKeyField.register_lookup(DateTimeLtLookup)
DatePGPSymmetricKeyField.register_lookup(DateTimeLteLookup)
DatePGPSymmetricKeyField.register_lookup(DateTimeGtLookup)
DatePGPSymmetricKeyField.register_lookup(DateTimeGteLookup)
DatePGPSymmetricKeyField.register_lookup(DateTimeRangeLookup)


class DateTimePGPSymmetricKeyField(DateTimePGPSymmetricKeyFieldMixin, models.TextField):
    """DateTime PGP symmetric key encrypted field for postgres."""


DateTimePGPSymmetricKeyField.register_lookup(DateTimeExactLookup)
DateTimePGPSymmetricKeyField.register_lookup(DateTimeLtLookup)
DateTimePGPSymmetricKeyField.register_lookup(DateTimeLteLookup)
DateTimePGPSymmetricKeyField.register_lookup(DateTimeGtLookup)
DateTimePGPSymmetricKeyField.register_lookup(DateTimeGteLookup)
DateTimePGPSymmetricKeyField.register_lookup(DateTimeRangeLookup)
