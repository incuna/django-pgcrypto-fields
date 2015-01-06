from django.db import models

from pgcrypto_fields import fields


class EncryptedModel(models.Model):
    """Dummy model used for tests to check the fields."""
    digest_field = fields.TextDigestField(blank=True, null=True)
    hmac_field = fields.TextHMACField(blank=True, null=True)

    email_pgp_pub_field = fields.EmailPGPPublicKeyField(blank=True, null=True)
    integer_pgp_pub_field = fields.IntegerPGPPublicKeyField(blank=True, null=True)
    pgp_pub_field = fields.TextPGPPublicKeyField(blank=True, null=True)

    email_pgp_sym_field = fields.EmailPGPSymmetricKeyField(blank=True, null=True)
    integer_pgp_sym_field = fields.IntegerPGPSymmetricKeyField(blank=True, null=True)
    pgp_sym_field = fields.TextPGPSymmetricKeyField(blank=True, null=True)
