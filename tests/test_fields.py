from django.test import TestCase
from django.test.utils import override_settings

from pgcrypto_fields import aggregates, fields
from .factories import EncryptedTextFieldModelFactory
from .models import EncryptedTextFieldModel


PUBLIC_PGP_KEY = 'my public key'


class TestEncryptedTextField(TestCase):
    """Test `EncryptedTextField` behave properly."""
    field = fields.EncryptedTextField

    def test_db_type(self):
        """Check db_type is `bytea`."""
        self.assertEqual(self.field().db_type(), 'bytea')

    @override_settings(PUBLIC_PGP_KEY=PUBLIC_PGP_KEY)
    def test_get_placeholder(self):
        """Check `get_placeholder` returns the right string function to encrypt data."""
        expected = "pgp_pub_encrypt(%s, dearmor('{}'))".format(PUBLIC_PGP_KEY)
        self.assertEqual(self.field().get_placeholder(), expected)

    def test_south_field_triple(self):
        """Check return a suitable description for south migration."""
        south_triple = fields.EncryptedTextField().south_field_triple()
        expected = ('pgcrypto_fields.fields.EncryptedTextField', [], {})
        self.assertEqual(south_triple, expected)


class TestEncryptedTextFieldModel(TestCase):
    """Test `EncryptedTextField` can be integrated in a `Django` model."""
    model = EncryptedTextFieldModel

    def test_fields(self):
        """Assert fields are representing our model."""
        fields = self.model._meta.get_all_field_names()
        expected = ('id', 'encrypted_value')
        self.assertCountEqual(fields, expected)

    def test_value_returned_is_bytea(self):
        """Assert value returned is a memoryview instance."""
        EncryptedTextFieldModelFactory.create()

        instance = EncryptedTextFieldModel.objects.get()
        self.assertIsInstance(instance.encrypted_value, memoryview)

    def test_value(self):
        """Assert we can get back the decrypted value."""
        expected = 'bonjour'
        EncryptedTextFieldModelFactory.create(encrypted_value=expected)

        queryset = EncryptedTextFieldModel.objects.annotate(
            aggregates.Decrypt('encrypted_value'),
        )
        instance = queryset.get()
        self.assertEqual(instance.encrypted_value__decrypt, expected)
