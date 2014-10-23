import factory


class EncryptedTextFieldModelFactory(factory.DjangoModelFactory):
    """Factory to generate `encrypted_value`."""
    encrypted_value = factory.Sequence('Text {}')
