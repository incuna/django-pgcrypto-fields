from django.db import models

from pgcrypto_fields import fields


class EncryptedTextFieldModel(models.Model):
    """Dummy model used for tests to check `EncryptedTextField`."""
    digest_field = fields.HashedTextField(fields.Digest)
    hmac_field = fields.HashedTextField(fields.HMAC)

    pgp_pub_field = fields.EncryptedTextField(fields.PGPPublicKey)
    pgp_sym_field = fields.EncryptedTextField(fields.PGPSymmetricKey)
