from django.db import models

from pgcrypto_fields import fields


class EncryptedTextFieldModel(models.Model):
    """Dummy model used for tests to check `EncryptedTextField`."""
    digest_field = fields.DigestField()
    hmac_field = fields.HMACField()

    pgp_pub_field = fields.PGPPublicKeyField()
    pgp_sym_field = fields.PGPSymmetricKeyField()
