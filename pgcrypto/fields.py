from django.db import models

from pgcrypto import (
    DIGEST_SQL,
    HMAC_SQL,
    INTEGER_PGP_PUB_ENCRYPT_SQL,
    INTEGER_PGP_SYM_ENCRYPT_SQL,
    PGP_PUB_ENCRYPT_SQL,
    PGP_SYM_ENCRYPT_SQL,
)
from pgcrypto.lookups import (
    DatePGPPublicKeyEXACT,
    DatePGPPublicKeyGT,
    DatePGPPublicKeyGTE,
    DatePGPPublicKeyLT,
    DatePGPPublicKeyLTE,
    DatePGPPublicKeyRANGE,
    DatePGPSymmetricKeyEXACT,
    DatePGPSymmetricKeyGT,
    DatePGPSymmetricKeyGTE,
    DatePGPSymmetricKeyLT,
    DatePGPSymmetricKeyLTE,
    DatePGPSymmetricKeyRANGE,
    DateTimePGPPublicKeyEXACT,
    DateTimePGPPublicKeyGT,
    DateTimePGPPublicKeyGTE,
    DateTimePGPPublicKeyLT,
    DateTimePGPPublicKeyLTE,
    DateTimePGPPublicKeyRANGE,
    DateTimePGPSymmetricKeyEXACT,
    DateTimePGPSymmetricKeyGT,
    DateTimePGPSymmetricKeyGTE,
    DateTimePGPSymmetricKeyLT,
    DateTimePGPSymmetricKeyLTE,
    DateTimePGPSymmetricKeyRANGE,
    DigestLookup,
    HMACLookup,
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


TextDigestField.register_lookup(DigestLookup)


class TextHMACField(HashMixin, models.TextField):
    """Text HMAC field for postgres."""
    encrypt_sql = HMAC_SQL


TextHMACField.register_lookup(HMACLookup)


class EmailPGPPublicKeyField(EmailPGPPublicKeyFieldMixin, models.EmailField):
    """Email PGP public key encrypted field."""
    encrypt_sql = PGP_PUB_ENCRYPT_SQL


class IntegerPGPPublicKeyField(PGPPublicKeyFieldMixin, models.IntegerField):
    """Integer PGP public key encrypted field."""
    encrypt_sql = INTEGER_PGP_PUB_ENCRYPT_SQL


class TextPGPPublicKeyField(PGPPublicKeyFieldMixin, models.TextField):
    """Text PGP public key encrypted field."""
    encrypt_sql = PGP_PUB_ENCRYPT_SQL


class DatePGPPublicKeyField(DatePGPPublicKeyFieldMixin, models.TextField):
    """Date PGP public key encrypted field for postgres."""
    encrypt_sql = PGP_PUB_ENCRYPT_SQL
    cast_sql = 'cast(%s as DATE)'


DatePGPPublicKeyField.register_lookup(DatePGPPublicKeyEXACT)
DatePGPPublicKeyField.register_lookup(DatePGPPublicKeyGT)
DatePGPPublicKeyField.register_lookup(DatePGPPublicKeyGTE)
DatePGPPublicKeyField.register_lookup(DatePGPPublicKeyLT)
DatePGPPublicKeyField.register_lookup(DatePGPPublicKeyLTE)
DatePGPPublicKeyField.register_lookup(DatePGPPublicKeyRANGE)


class DateTimePGPPublicKeyField(DateTimePGPPublicKeyFieldMixin, models.TextField):
    """DateTime PGP public key encrypted field for postgres."""
    encrypt_sql = PGP_PUB_ENCRYPT_SQL
    cast_sql = 'cast(%s as TIMESTAMP)'


DateTimePGPPublicKeyField.register_lookup(DateTimePGPPublicKeyEXACT)
DateTimePGPPublicKeyField.register_lookup(DateTimePGPPublicKeyGT)
DateTimePGPPublicKeyField.register_lookup(DateTimePGPPublicKeyGTE)
DateTimePGPPublicKeyField.register_lookup(DateTimePGPPublicKeyLT)
DateTimePGPPublicKeyField.register_lookup(DateTimePGPPublicKeyLTE)
DateTimePGPPublicKeyField.register_lookup(DateTimePGPPublicKeyRANGE)


class EmailPGPSymmetricKeyField(EmailPGPSymmetricKeyFieldMixin, models.EmailField):
    """Email PGP symmetric key encrypted field."""
    encrypt_sql = PGP_SYM_ENCRYPT_SQL


class IntegerPGPSymmetricKeyField(PGPSymmetricKeyFieldMixin, models.IntegerField):
    """Integer PGP symmetric key encrypted field."""
    encrypt_sql = INTEGER_PGP_SYM_ENCRYPT_SQL


class TextPGPSymmetricKeyField(PGPSymmetricKeyFieldMixin, models.TextField):
    """Text PGP symmetric key encrypted field for postgres."""
    encrypt_sql = PGP_SYM_ENCRYPT_SQL


class DatePGPSymmetricKeyField(DatePGPSymmetricKeyFieldMixin, models.TextField):
    """Date PGP symmetric key encrypted field for postgres."""
    encrypt_sql = PGP_SYM_ENCRYPT_SQL
    cast_sql = 'cast(%s as DATE)'


DatePGPSymmetricKeyField.register_lookup(DatePGPSymmetricKeyEXACT)
DatePGPSymmetricKeyField.register_lookup(DatePGPSymmetricKeyGT)
DatePGPSymmetricKeyField.register_lookup(DatePGPSymmetricKeyGTE)
DatePGPSymmetricKeyField.register_lookup(DatePGPSymmetricKeyLT)
DatePGPSymmetricKeyField.register_lookup(DatePGPSymmetricKeyLTE)
DatePGPSymmetricKeyField.register_lookup(DatePGPSymmetricKeyRANGE)


class DateTimePGPSymmetricKeyField(DateTimePGPSymmetricKeyFieldMixin, models.TextField):
    """DateTime PGP symmetric key encrypted field for postgres."""
    encrypt_sql = PGP_SYM_ENCRYPT_SQL
    cast_sql = 'cast(%s as TIMESTAMP)'


DateTimePGPSymmetricKeyField.register_lookup(DateTimePGPSymmetricKeyEXACT)
DateTimePGPSymmetricKeyField.register_lookup(DateTimePGPSymmetricKeyGT)
DateTimePGPSymmetricKeyField.register_lookup(DateTimePGPSymmetricKeyGTE)
DateTimePGPSymmetricKeyField.register_lookup(DateTimePGPSymmetricKeyLT)
DateTimePGPSymmetricKeyField.register_lookup(DateTimePGPSymmetricKeyLTE)
DateTimePGPSymmetricKeyField.register_lookup(DateTimePGPSymmetricKeyRANGE)
