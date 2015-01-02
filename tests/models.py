from django.db import models

from pgcrypto_fields import fields


class EncryptedTextFieldModel(models.Model):
    """Dummy model used for tests to check `EncryptedTextField`."""
    digest_field = fields.TextDigestField()
    hmac_field = fields.TextHMACField()

    integer_pgp_pub_field = fields.IntegerPGPPublicKeyField()
    pgp_pub_field = fields.TextPGPPublicKeyField()
    integer_pgp_sym_field = fields.IntegerPGPSymmetricKeyField()
    pgp_sym_field = fields.TextPGPSymmetricKeyField()
