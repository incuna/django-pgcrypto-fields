from django.db import models

from pgcrypto_fields.fields import EncryptedTextField


class EncryptedTextFieldModel(models.Model):
    """Dummy model used for tests to check `EncryptedTextField`."""
    encrypted_value = EncryptedTextField()
