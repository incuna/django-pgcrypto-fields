from django.test import TestCase

from pgcrypto_fields import aggregates, fields, proxy

from .factories import EncryptedTextFieldModelFactory
from .models import EncryptedTextFieldModel


class TestTextFieldBase(TestCase):
    """Test `EncryptedTextField` behave properly."""
    field = fields.TextFieldBase

    def test_db_type(self):
        """Check db_type is `bytea`."""
        self.assertEqual(self.field().db_type(), 'bytea')


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

        instance = self.model.objects.get()
        self.assertIsInstance(instance.digest_field, memoryview)
        self.assertIsInstance(instance.hmac_field, memoryview)

        self.assertIsInstance(instance.pgp_pub_field, memoryview)
        self.assertIsInstance(instance.pgp_sym_field, memoryview)

    def test_fields_descriptor_is_not_instance(self):
        """`EncryptedProxyField` instance returns itself when accessed from the model."""
        self.assertIsInstance(
            self.model.pgp_pub_field_decrypted,
            proxy.EncryptedProxyField,
        )
        self.assertIsInstance(
            self.model.pgp_sym_field_decrypted,
            proxy.EncryptedProxyField,
        )

    def test_value_query(self):
        """Assert querying the field's value is making one query."""
        expected = 'bonjour'
        EncryptedTextFieldModelFactory.create(pgp_pub_field=expected)

        instance = self.model.objects.get()

        with self.assertNumQueries(1):
            instance.pgp_pub_field_decrypted

    def test_value_pgp_pub(self):
        """Assert we can get back the decrypted value."""
        expected = 'bonjour'
        EncryptedTextFieldModelFactory.create(pgp_pub_field=expected)

        instance = self.model.objects.get()
        value = instance.pgp_pub_field_decrypted

        self.assertEqual(value, expected)

    def test_value_pgp_pub_multipe(self):
        """Assert we get back the correct value when the table contains data."""
        expected = 'bonjour'
        EncryptedTextFieldModelFactory.create(pgp_pub_field='au revoir')
        created = EncryptedTextFieldModelFactory.create(pgp_pub_field=expected)

        instance = self.model.objects.get(pk=created.pk)
        value = instance.pgp_pub_field_decrypted

        self.assertEqual(value, expected)

    def test_value_pgp_sym(self):
        """Assert we can get back the decrypted value."""
        expected = 'bonjour'
        EncryptedTextFieldModelFactory.create(pgp_sym_field=expected)

        instance = self.model.objects.get()
        value = instance.pgp_sym_field_decrypted

        self.assertEqual(value, expected)

    def test_instance_not_saved(self):
        """Assert not saved instance return the value to be encrypted."""
        expected = 'bonjour'
        instance = EncryptedTextFieldModelFactory.build(pgp_pub_field=expected)
        self.assertEqual(instance.pgp_pub_field_decrypted, expected)
        self.assertEqual(instance.pgp_pub_field, expected)

    def test_decrypt_annotate(self):
        """Assert we can get back the decrypted value."""
        expected = 'bonjour'
        EncryptedTextFieldModelFactory.create(
            pgp_pub_field=expected,
            pgp_sym_field=expected,
        )

        queryset = self.model.objects.annotate(
            aggregates.PGPPublicKeyAggregate('pgp_pub_field'),
            aggregates.PGPSymmetricKeyAggregate('pgp_sym_field'),
        )
        instance = queryset.get()
        self.assertEqual(instance.pgp_pub_field__decrypted, expected)
        self.assertEqual(instance.pgp_sym_field__decrypted, expected)

    def test_decrypt_filter(self):
        """Assert we can get filter the decrypted value."""
        expected = 'bonjour'
        EncryptedTextFieldModelFactory.create(
            pgp_pub_field=expected,
        )

        queryset = self.model.objects.annotate(
            aggregates.PGPPublicKeyAggregate('pgp_pub_field'),
        )
        instance = queryset.filter(pgp_pub_field__decrypted=expected).first()
        self.assertEqual(instance.pgp_pub_field__decrypted, expected)

    def test_digest_lookup(self):
        """Assert we can filter a digest value."""
        value = 'bonjour'
        expected = EncryptedTextFieldModelFactory.create(digest_field=value)
        EncryptedTextFieldModelFactory.create()

        queryset = EncryptedTextFieldModel.objects.filter(digest_field__hash_of=value)

        self.assertCountEqual(queryset, [expected])

    def test_hmac_lookup(self):
        """Assert we can filter a digest value."""
        value = 'bonjour'
        expected = EncryptedTextFieldModelFactory.create(hmac_field=value)
        EncryptedTextFieldModelFactory.create()

        queryset = EncryptedTextFieldModel.objects.filter(hmac_field__hash_of=value)
        self.assertCountEqual(queryset, [expected])

    def test_default_lookup(self):
        """Assert default lookup can be called."""
        queryset = EncryptedTextFieldModel.objects.filter(hmac_field__isnull=True)
        self.assertFalse(queryset)

    def test_update_attribute_digest_field(self):
        """Assert digest field can be updated through its attribute on the model."""
        expected = 'bonjour'
        instance = EncryptedTextFieldModelFactory.create()
        instance.digest_field = expected
        instance.save()

        updated_instance = self.model.objects.filter(digest_field__hash_of=expected)
        self.assertEqual(updated_instance.first(), instance)

    def test_update_attribute_hmac_field(self):
        """Assert hmac field can be updated through its attribute on the model."""
        expected = 'bonjour'
        instance = EncryptedTextFieldModelFactory.create()
        instance.hmac_field = expected
        instance.save()

        updated_instance = self.model.objects.filter(hmac_field__hash_of=expected)
        self.assertEqual(updated_instance.first(), instance)

    def test_update_attribute_pgp_pub_field(self):
        """Assert pgp field can be updated through its attribute on the model."""
        expected = 'bonjour'
        instance = EncryptedTextFieldModelFactory.create()
        instance.pgp_pub_field = expected
        instance.save()

        updated_instance = self.model.objects.get()
        self.assertEqual(updated_instance.pgp_pub_field_decrypted, expected)

    def test_update_attribute_pgp_sym_field(self):
        """Assert pgp field can be updated through its attribute on the model."""
        expected = 'bonjour'
        instance = EncryptedTextFieldModelFactory.create()
        instance.pgp_sym_field = expected
        instance.save()

        updated_instance = self.model.objects.get()
        self.assertEqual(updated_instance.pgp_sym_field_decrypted, expected)
