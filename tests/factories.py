import factory

from .models import EncryptedTextFieldModel


class EncryptedTextFieldModelFactory(factory.DjangoModelFactory):
    """Factory to generate `encrypted_value`."""
    class Meta:
        model = EncryptedTextFieldModel

    encrypted_value = factory.Sequence('Text {}'.format)
