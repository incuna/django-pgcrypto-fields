import factory

from .models import EncryptedTextFieldModel


class EncryptedTextFieldModelFactory(factory.DjangoModelFactory):
    """Factory to generate hashed and encrypted data."""
    class Meta:
        model = EncryptedTextFieldModel

    digest_field = factory.Sequence('Text digest {}'.format)
    hmac_field = factory.Sequence('Text hmac {}'.format)

    integer_pgp_pub_field = 42
    pgp_pub_field = factory.Sequence('Text with public key {}'.format)
    integer_pgp_sym_field = 43
    pgp_sym_field = factory.Sequence('Text with symmetric key {}'.format)
