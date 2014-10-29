from django.db import models

from pgcrypto_fields.fields import EncryptedTextField, ENCRYPTION_TYPES


class EncryptedTextFieldModel(models.Model):
    """Dummy model used for tests to check `EncryptedTextField`."""
    digest_field = EncryptedTextField(ENCRYPTION_TYPES['digest'])
    hmac_field = EncryptedTextField(ENCRYPTION_TYPES['hmac'])
    pgp_pub_field = EncryptedTextField(ENCRYPTION_TYPES['pgp_pub'])
    pgp_sym_field = EncryptedTextField(ENCRYPTION_TYPES['pgp_sym'])
