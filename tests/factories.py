import factory

from .models import EncryptedModel


class EncryptedModelFactory(factory.DjangoModelFactory):
    """Factory to generate hashed and encrypted data."""
    class Meta:
        model = EncryptedModel

    digest_field = factory.Sequence('Text digest {}'.format)
    hmac_field = factory.Sequence('Text hmac {}'.format)

    email_pgp_pub_field = factory.Sequence('email{}@public.key'.format)
    integer_pgp_pub_field = 42
    pgp_pub_field = factory.Sequence('Text with public key {}'.format)

    email_pgp_sym_field = factory.Sequence('email{}@symmetric.key'.format)
    integer_pgp_sym_field = 43
    pgp_sym_field = factory.Sequence('Text with symmetric key {}'.format)
