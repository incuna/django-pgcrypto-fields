from django.db import models

from pgcrypto_fields import functions
from pgcrypto_fields.fields import EncryptedTextField, HashedTextField


class EncryptedTextFieldModel(models.Model):
    """Dummy model used for tests to check `EncryptedTextField`."""
    digest_field = HashedTextField(encryption_method=functions.Digest)
    hmac_field = HashedTextField(encryption_method=functions.HMAC)

    pgp_pub_field = EncryptedTextField(encryption_method=functions.PGPPub)
    pgp_sym_field = EncryptedTextField(encryption_method=functions.PGPSym)
