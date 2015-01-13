from django.db import models

from pgcrypto_fields import (
    DIGEST_SQL,
    HMAC_SQL,
    INTEGER_PGP_PUB_ENCRYPT_SQL,
    INTEGER_PGP_SYM_ENCRYPT_SQL,
    PGP_PUB_ENCRYPT_SQL,
    PGP_SYM_ENCRYPT_SQL,
)
from pgcrypto_fields.lookups import DigestLookup, HMACLookup
from pgcrypto_fields.mixins import (
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


class EmailPGPSymmetricKeyField(EmailPGPSymmetricKeyFieldMixin, models.EmailField):
    """Email PGP symmetric key encrypted field."""
    encrypt_sql = PGP_SYM_ENCRYPT_SQL


class IntegerPGPSymmetricKeyField(PGPSymmetricKeyFieldMixin, models.IntegerField):
    """Integer PGP symmetric key encrypted field."""
    encrypt_sql = INTEGER_PGP_SYM_ENCRYPT_SQL


class TextPGPSymmetricKeyField(PGPSymmetricKeyFieldMixin, models.TextField):
    """Text PGP symmetric key encrypted field for postgres."""
    encrypt_sql = PGP_SYM_ENCRYPT_SQL
