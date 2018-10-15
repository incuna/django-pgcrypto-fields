from django.db import models

from pgcrypto import fields


class EncryptedFKModel(models.Model):
    """Dummy model used to test FK decryption."""
    fk_pgp_sym_field = fields.TextPGPSymmetricKeyField(blank=True, null=True)

    class Meta:
        """Sets up the meta for the test model."""
        app_label = 'tests'


class EncryptedModelManager(models.Manager):

    def get_by_natural_key(self, email_pgp_pub_field):
        """Get by natual key of email pub field."""
        return self.get(email_pgp_pub_field=email_pgp_pub_field)


class EncryptedModel(models.Model):
    """Dummy model used for tests to check the fields."""
    digest_field = fields.TextDigestField(blank=True, null=True)
    digest_with_original_field = fields.TextDigestField(blank=True, null=True,
                                                        original='pgp_sym_field')
    hmac_field = fields.TextHMACField(blank=True, null=True)
    hmac_with_original_field = fields.TextHMACField(blank=True, null=True,
                                                    original='pgp_sym_field')

    email_pgp_pub_field = fields.EmailPGPPublicKeyField(blank=True, null=True,
                                                        unique=True)
    integer_pgp_pub_field = fields.IntegerPGPPublicKeyField(blank=True, null=True)
    pgp_pub_field = fields.TextPGPPublicKeyField(blank=True, null=True)
    date_pgp_pub_field = fields.DatePGPPublicKeyField(blank=True, null=True)
    datetime_pgp_pub_field = fields.DateTimePGPPublicKeyField(blank=True, null=True)
    decimal_pgp_pub_field = fields.DecimalPGPPublicKeyField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    email_pgp_sym_field = fields.EmailPGPSymmetricKeyField(blank=True, null=True)
    integer_pgp_sym_field = fields.IntegerPGPSymmetricKeyField(blank=True, null=True)
    pgp_sym_field = fields.TextPGPSymmetricKeyField(blank=True, null=True)
    date_pgp_sym_field = fields.DatePGPSymmetricKeyField(blank=True, null=True)
    datetime_pgp_sym_field = fields.DateTimePGPSymmetricKeyField(blank=True, null=True)
    decimal_pgp_sym_field = fields.DecimalPGPSymmetricKeyField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    fk_model = models.ForeignKey(
        EncryptedFKModel, blank=True, null=True, on_delete=models.CASCADE
    )

    objects = EncryptedModelManager()

    class Meta:
        """Sets up the meta for the test model."""
        app_label = 'tests'


class EncryptedDateTime(models.Model):
    value = fields.DateTimePGPSymmetricKeyField()


class RelatedDateTime(models.Model):
    related = models.ForeignKey(
        EncryptedDateTime,
        on_delete=models.CASCADE,
        related_name='related')
    related_again = models.ForeignKey(
        EncryptedDateTime, null=True,
        on_delete=models.CASCADE, related_name='related_again'
    )
