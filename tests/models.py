from django.db import models

from pgcrypto_fields import fields


class EncryptedTextFieldModel(models.Model):
    """Dummy model used for tests to check `EncryptedTextField`."""
    digest_field = fields.HashedTextField(fields.DIGEST)
    hmac_field = fields.HashedTextField(fields.HMAC)

    pgp_pub_field = fields.EncryptedTextField(fields.PGP_PUB)
    pgp_sym_field = fields.EncryptedTextField(fields.PGP_SYM)
