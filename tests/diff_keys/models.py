from django.db import models

from pgcrypto import fields


class EncryptedDiff(models.Model):
    CHOICES = (
        ('a', 'a'),
        (1, '1'),
    )
    pub_field = fields.CharPGPPublicKeyField(blank=True, null=True,
                                             choices=CHOICES, max_length=1)
    sym_field = fields.CharPGPSymmetricKeyField(blank=True, null=True,
                                                choices=CHOICES, max_length=1)
    digest_field = fields.TextDigestField(blank=True, null=True)
    hmac_field = fields.TextHMACField(blank=True, null=True)

    class Meta:
        """Sets up the meta for the test model."""
        app_label = 'diff_keys'
