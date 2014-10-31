from django.db import models

from pgcrypto_fields import aggregates, fields


class EncryptedTextFieldModel(models.Model):
    """Dummy model used for tests to check `EncryptedTextField`."""
    digest_field = fields.HashedTextField(aggregates.Digest)
    hmac_field = fields.HashedTextField(aggregates.HMAC)

    pgp_pub_field = fields.EncryptedTextField(aggregates.PGPPublicKey)
    pgp_sym_field = fields.EncryptedTextField(aggregates.PGPSymmetricKey)
