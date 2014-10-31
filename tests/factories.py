import factory

from .models import EncryptedTextFieldModel


class EncryptedTextFieldModelFactory(factory.DjangoModelFactory):
    """Factory to generate hashed and encrypted data."""
    class Meta:
        model = EncryptedTextFieldModel

    digest_field = factory.Sequence('Text digest {}'.format)
    hmac_field = factory.Sequence('Text hmac {}'.format)
    pgp_pub_field = factory.Sequence('Text with public key {}'.format)
    pgp_sym_field = factory.Sequence('Text with symmetric key {}'.format)
