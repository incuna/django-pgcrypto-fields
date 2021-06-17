from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import factory

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
    datetime_pgp_pub_field = datetime.now()
    decimal_pgp_pub_field = Decimal('123456.78')
    boolean_pgp_pub_field = True
    uuid_pgp_pub_field = uuid4()

    email_pgp_sym_field = factory.Sequence('email{}@symmetric.key'.format)
    integer_pgp_sym_field = 43
    biginteger_pgp_sym_field = 9223372036854775807
    pgp_sym_field = factory.Sequence('Text with symmetric key {}'.format)
    char_sym_field = factory.Sequence('Text {}'.format)

    date_pgp_sym_field = date.today()
    datetime_pgp_sym_field = datetime.now()
    boolean_pgp_sym_field = False
    uuid_pgp_sym_field = uuid4()

    fk_model = factory.SubFactory(EncryptedFKModelFactory)

    class Meta:
        """Sets up meta for test factory."""
        model = EncryptedModel
