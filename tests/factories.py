from datetime import date
from decimal import Decimal

import factory
from django.utils import timezone


from .models import EncryptedFKModel, EncryptedModel


class EncryptedFKModelFactory(factory.django.DjangoModelFactory):
    """Factory to generate foreign key data."""
    fk_pgp_sym_field = factory.Sequence('Text with symmetric key {}'.format)

    class Meta:
        """Sets up meta for test factory."""
        model = EncryptedFKModel


class EncryptedModelFactory(factory.django.DjangoModelFactory):
    """Factory to generate hashed and encrypted data."""

    digest_field = factory.Sequence('Text digest {}'.format)
    hmac_field = factory.Sequence('Text hmac {}'.format)

    email_pgp_pub_field = factory.Sequence('email{}@public.key'.format)
    integer_pgp_pub_field = 42
    biginteger_pgp_pub_field = 9223372036854775807
    pgp_pub_field = factory.Sequence('Text with public key {}'.format)
    char_pub_field = factory.Sequence('Text {}'.format)

    date_pgp_pub_field = date.today()
    datetime_pgp_pub_field = timezone.now()
    decimal_pgp_pub_field = Decimal('123456.78')
    boolean_pgp_pub_field = True

    email_pgp_sym_field = factory.Sequence('email{}@symmetric.key'.format)
    integer_pgp_sym_field = 43
    biginteger_pgp_sym_field = 9223372036854775807
    pgp_sym_field = factory.Sequence('Text with symmetric key {}'.format)
    char_sym_field = factory.Sequence('Text {}'.format)

    date_pgp_sym_field = date.today()
    datetime_pgp_sym_field = timezone.now()
    boolean_pgp_sym_field = False

    json_pgp_pub_field = {"key": "value"}
    json_pgp_sym_field = {"key": "value"}

    fk_model = factory.SubFactory(EncryptedFKModelFactory)

    class Meta:
        """Sets up meta for test factory."""
        model = EncryptedModel
