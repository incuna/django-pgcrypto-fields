from datetime import date, datetime

import factory

from .models import EncryptedFKModel, EncryptedModel


class EncryptedFKModelFactory(factory.DjangoModelFactory):
    """Factory to generate foreign key data."""
    fk_pgp_sym_field = factory.Sequence('Text with symmetric key {}'.format)

    class Meta:
        """Sets up meta for test factory."""
        model = EncryptedFKModel


class EncryptedModelFactory(factory.DjangoModelFactory):
    """Factory to generate hashed and encrypted data."""

    digest_field = factory.Sequence('Text digest {}'.format)
    hmac_field = factory.Sequence('Text hmac {}'.format)

    email_pgp_pub_field = factory.Sequence('email{}@public.key'.format)
    integer_pgp_pub_field = 42
    pgp_pub_field = factory.Sequence('Text with public key {}'.format)

    date_pgp_pub_field = date.today()
    datetime_pgp_pub_field = datetime.now()

    email_pgp_sym_field = factory.Sequence('email{}@symmetric.key'.format)
    integer_pgp_sym_field = 43
    pgp_sym_field = factory.Sequence('Text with symmetric key {}'.format)

    date_pgp_sym_field = date.today()
    datetime_pgp_sym_field = datetime.now()

    fk_model = factory.SubFactory(EncryptedFKModelFactory)

    class Meta:
        """Sets up meta for test factory."""
        model = EncryptedModel
