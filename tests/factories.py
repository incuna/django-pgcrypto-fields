import factory

from .models import EncryptedTextFieldModel


class EncryptedTextFieldModelFactory(factory.DjangoModelFactory):
    """Factory to generate `pgp_pub_field`."""
    class Meta:
        model = EncryptedTextFieldModel

    pgp_pub_field = factory.Sequence('Text with public key {}'.format)
    digest_field = factory.Sequence('Text digest {}'.format)
