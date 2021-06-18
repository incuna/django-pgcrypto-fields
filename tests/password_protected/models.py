from django.db import models

from pgcrypto import fields


class EncryptedPasswordProtected(models.Model):
    pub_field = fields.CharPGPPublicKeyField(blank=True, null=True, max_length=10)

    class Meta:
        """Sets up the meta for the test model."""
        app_label = 'password_protected'
