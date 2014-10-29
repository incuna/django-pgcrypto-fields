from django.conf import settings
from django.test import TestCase

from pgcrypto_fields import aggregates, fields
from .factories import EncryptedTextFieldModelFactory
from .models import EncryptedTextFieldModel


class TestEncryptedTextField(TestCase):
    """Test `EncryptedTextField` behave properly."""
    field = fields.EncryptedTextField

    def test_db_type(self):
        """Check db_type is `bytea`."""
        self.assertEqual(self.field().db_type(), 'bytea')

    def test_get_placeholder(self):
        """Check `get_placeholder` returns the right string function to encrypt data."""
        expected = "pgp_pub_encrypt(%s, dearmor('{}'))".format(settings.PUBLIC_PGP_KEY)
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
        expected = (
            'id',
            'digest_field',
            'hmac_field',
            'pgp_pub_field',
            'pgp_sym_field',
        )
        self.assertCountEqual(fields, expected)

    def test_value_returned_is_bytea(self):
        """Assert value returned is a memoryview instance."""
        EncryptedTextFieldModelFactory.create()

        instance = EncryptedTextFieldModel.objects.get()
        self.assertIsInstance(instance.digest_field_raw, memoryview)
        self.assertIsInstance(instance.hmac_field_raw, memoryview)
        self.assertIsInstance(instance.pgp_pub_field_raw, memoryview)
        self.assertIsInstance(instance.pgp_sym_field_raw, memoryview)

    def test_value(self):
        """Assert we can get back the decrypted value."""
        expected = 'bonjour'
        EncryptedTextFieldModelFactory.create(pgp_pub_field=expected)

        instance = EncryptedTextFieldModel.objects.get()

        with self.assertNumQueries(1):
            value = instance.pgp_pub_field

        self.assertEqual(value, expected)

    def test_instance_not_saved(self):
        """Assert not saved instance return the value to be encrypted."""
        expected = 'bonjour'
        instance = EncryptedTextFieldModelFactory.build(pgp_pub_field=expected)
        self.assertEqual(instance.pgp_pub_field, expected)
        self.assertEqual(instance.pgp_pub_field_raw, expected)

    def test_decrypt_annotate(self):
        """Assert we can get back the decrypted value."""
        expected = 'bonjour'
        EncryptedTextFieldModelFactory.create(pgp_pub_field=expected)

        queryset = EncryptedTextFieldModel.objects.annotate(
            aggregates.Decrypt('pgp_pub_field'),
        )
        instance = queryset.get()
        self.assertEqual(instance.pgp_pub_field__decrypt, expected)
