from django.db import models

from pgcrypto import fields


class EncryptedDiff(models.Model):
    pub_field = fields.TextPGPPublicKeyField()
    sym_field = fields.TextPGPSymmetricKeyField()
    digest_field = fields.TextDigestField(blank=True, null=True)
    hmac_field = fields.TextHMACField(blank=True, null=True)

    class Meta:
        """Sets up the meta for the test model."""
        app_label = 'diff_keys'
