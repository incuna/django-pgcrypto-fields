from django.db import models

from pgcrypto import fields, managers


class EncryptedModelManager(managers.PGPManager):
    pass


class EncryptedModel(models.Model):
    """Dummy model used for tests to check the fields."""
    digest_field = fields.TextDigestField(blank=True, null=True)
    digest_with_original_field = fields.TextDigestField(blank=True, null=True,
                                                        original='pgp_sym_field')
    hmac_field = fields.TextHMACField(blank=True, null=True)
    hmac_with_original_field = fields.TextHMACField(blank=True, null=True,
                                                    original='pgp_sym_field')

    email_pgp_pub_field = fields.EmailPGPPublicKeyField(blank=True, null=True)
    integer_pgp_pub_field = fields.IntegerPGPPublicKeyField(blank=True, null=True)
    pgp_pub_field = fields.TextPGPPublicKeyField(blank=True, null=True)

    email_pgp_sym_field = fields.EmailPGPSymmetricKeyField(blank=True, null=True)
    integer_pgp_sym_field = fields.IntegerPGPSymmetricKeyField(blank=True, null=True)
    pgp_sym_field = fields.TextPGPSymmetricKeyField(blank=True, null=True)
    date_pgp_sym_field = fields.DatePGPSymmetricKeyField(blank=True, null=True)
    datetime_pgp_sym_field = fields.DateTimePGPSymmetricKeyField(blank=True, null=True)

    class Meta:
        """Sets up the meta for the test model."""
        app_label = 'tests'


class EncryptedModelWithManager(EncryptedModel):

    objects = EncryptedModelManager()

    class Meta:
        """Sets up the meta for the test manager."""
        proxy = True
