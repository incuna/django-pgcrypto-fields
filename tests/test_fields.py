from django.test import TestCase

from pgcrypto_fields import aggregates, proxy
from pgcrypto_fields import fields

from .factories import EncryptedModelFactory
from .models import EncryptedModel

PGP_FIELDS = (
    fields.EmailPGPPublicKeyField,
    fields.EmailPGPSymmetricKeyField,
    fields.IntegerPGPPublicKeyField,
    fields.IntegerPGPSymmetricKeyField,
    fields.TextPGPPublicKeyField,
    fields.TextPGPSymmetricKeyField,
)


class TestTextFieldHash(TestCase):
    """Test `TextFieldHash` behave properly."""
    field = fields.TextFieldHash

    def test_get_placeholder(self):
        """Assert `get_placeholder` hash value only once."""
        placeholder = self.field().get_placeholder('\\x')
        self.assertEqual(placeholder, '%s')


class TestPGPMixin(TestCase):
    """Test `PGPMixin` behave properly."""

    def test_check(self):
        """Assert `max_length` check does not return any error."""
        for field in PGP_FIELDS:
            with self.subTest(field=field):
                self.assertEqual(field(name='field').check(), [])

    def test_max_length(self):
        """Assert `max_length` is ignored."""
        for field in PGP_FIELDS:
            with self.subTest(field=field):
                self.assertEqual(field(max_length=42).max_length, None)

    def test_db_type(self):
        """Check db_type is `bytea`."""
        for field in PGP_FIELDS:
            with self.subTest(field=field):
                self.assertEqual(field().db_type(), 'bytea')


class TestEncryptedTextFieldModel(TestCase):
    """Test `EncryptedTextField` can be integrated in a `Django` model."""
    model = EncryptedModel

    def test_fields(self):
        """Assert fields are representing our model."""
        fields = self.model._meta.get_all_field_names()
        expected = (
            'id',
            'digest_field',
            'hmac_field',
            'email_pgp_pub_field',
            'integer_pgp_pub_field',
            'pgp_pub_field',
            'email_pgp_sym_field',
            'integer_pgp_sym_field',
            'pgp_sym_field',
        )
        self.assertCountEqual(fields, expected)

    def test_value_returned_is_not_bytea(self):
        """Assert value returned is not a memoryview instance."""
        EncryptedModelFactory.create()

        instance = self.model.objects.get()
        self.assertIsInstance(instance.digest_field, str)
        self.assertIsInstance(instance.hmac_field, str)

        self.assertIsInstance(instance.email_pgp_pub_field, str)
        self.assertIsInstance(instance.integer_pgp_pub_field, int)
        self.assertIsInstance(instance.pgp_pub_field, str)

        self.assertIsInstance(instance.email_pgp_sym_field, str)
        self.assertIsInstance(instance.integer_pgp_sym_field, int)
        self.assertIsInstance(instance.pgp_sym_field, str)

    def test_fields_descriptor_is_not_instance(self):
        """`EncryptedProxyField` instance returns itself when accessed from the model."""
        self.assertIsInstance(
            self.model.pgp_pub_field,
            proxy.EncryptedProxyField,
        )
        self.assertIsInstance(
            self.model.pgp_sym_field,
            proxy.EncryptedProxyField,
        )

    def test_value_query(self):
        """Assert querying the field's value is making one query."""
        expected = 'bonjour'
        EncryptedModelFactory.create(pgp_pub_field=expected)

        instance = self.model.objects.get()

        with self.assertNumQueries(1):
            instance.pgp_pub_field

    def test_value_pgp_pub(self):
        """Assert we can get back the decrypted value."""
        expected = 'bonjour'
        EncryptedModelFactory.create(pgp_pub_field=expected)

        instance = self.model.objects.get()
        value = instance.pgp_pub_field

        self.assertEqual(value, expected)

    def test_value_pgp_pub_multipe(self):
        """Assert we get back the correct value when the table contains data."""
        expected = 'bonjour'
        EncryptedModelFactory.create(pgp_pub_field='au revoir')
        created = EncryptedModelFactory.create(pgp_pub_field=expected)

        instance = self.model.objects.get(pk=created.pk)
        value = instance.pgp_pub_field

        self.assertEqual(value, expected)

    def test_value_pgp_sym(self):
        """Assert we can get back the decrypted value."""
        expected = 'bonjour'
        EncryptedModelFactory.create(pgp_sym_field=expected)

        instance = self.model.objects.get()
        value = instance.pgp_sym_field

        self.assertEqual(value, expected)

    def test_instance_not_saved(self):
        """Assert not saved instance return the value to be encrypted."""
        expected = 'bonjour'
        instance = EncryptedModelFactory.build(pgp_pub_field=expected)
        self.assertEqual(instance.pgp_pub_field, expected)
        self.assertEqual(instance.pgp_pub_field, expected)

    def test_decrypt_annotate(self):
        """Assert we can get back the decrypted value."""
        expected = 'bonjour'
        EncryptedModelFactory.create(
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
        EncryptedModelFactory.create(
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
        expected = EncryptedModelFactory.create(digest_field=value)
        EncryptedModelFactory.create()

        queryset = EncryptedModel.objects.filter(digest_field__hash_of=value)

        self.assertCountEqual(queryset, [expected])

    def test_hmac_lookup(self):
        """Assert we can filter a digest value."""
        value = 'bonjour'
        expected = EncryptedModelFactory.create(hmac_field=value)
        EncryptedModelFactory.create()

        queryset = EncryptedModel.objects.filter(hmac_field__hash_of=value)
        self.assertCountEqual(queryset, [expected])

    def test_default_lookup(self):
        """Assert default lookup can be called."""
        queryset = EncryptedModel.objects.filter(hmac_field__isnull=True)
        self.assertFalse(queryset)

    def test_update_attribute_digest_field(self):
        """Assert digest field can be updated through its attribute on the model."""
        expected = 'bonjour'
        instance = EncryptedModelFactory.create()
        instance.digest_field = expected
        instance.save()

        updated_instance = self.model.objects.filter(digest_field__hash_of=expected)
        self.assertEqual(updated_instance.first(), instance)

    def test_update_attribute_hmac_field(self):
        """Assert hmac field can be updated through its attribute on the model."""
        expected = 'bonjour'
        instance = EncryptedModelFactory.create()
        instance.hmac_field = expected
        instance.save()

        updated_instance = self.model.objects.filter(hmac_field__hash_of=expected)
        self.assertEqual(updated_instance.first(), instance)

    def test_update_attribute_pgp_pub_field(self):
        """Assert pgp field can be updated through its attribute on the model."""
        expected = 'bonjour'
        instance = EncryptedModelFactory.create()
        instance.pgp_pub_field = expected
        instance.save()

        updated_instance = self.model.objects.get()
        self.assertEqual(updated_instance.pgp_pub_field, expected)

    def test_update_attribute_pgp_sym_field(self):
        """Assert pgp field can be updated through its attribute on the model."""
        expected = 'bonjour'
        instance = EncryptedModelFactory.create()
        instance.pgp_sym_field = expected
        instance.save()

        updated_instance = self.model.objects.get()
        self.assertEqual(updated_instance.pgp_sym_field, expected)

    def test_update_one_attribute(self):
        """Assert value are not overriden when updating one attribute."""
        expected = 'initial value'
        new_value = 'new_value'

        instance = EncryptedModelFactory.create(
            pgp_pub_field=expected,
            pgp_sym_field=expected,
            digest_field=expected,
            hmac_field=expected,
        )
        instance.pgp_sym_field = new_value
        instance.save()

        updated_instance = self.model.objects.get()
        self.assertEqual(updated_instance.pgp_pub_field, expected)
        self.assertEqual(updated_instance.pgp_sym_field, new_value)

        updated_instance = self.model.objects.filter(
            digest_field__hash_of=expected,
            hmac_field__hash_of=expected,
        )
        self.assertEqual(updated_instance.first(), instance)

    def test_pgp_public_key_negative_number(self):
        """Assert negative value is saved with an `IntegerPGPPublicKeyField` field."""
        expected = -1
        instance = EncryptedModelFactory.create(integer_pgp_pub_field=expected)

        self.assertEqual(instance.integer_pgp_pub_field, expected)

    def test_pgp_symmetric_key_negative_number(self):
        """Assert negative value is saved with an `IntegerPGPSymmetricKeyField` field."""
        expected = -1
        instance = EncryptedModelFactory.create(integer_pgp_sym_field=expected)

        self.assertEqual(instance.integer_pgp_sym_field, expected)

    def test_digest_null(self):
        """Assert `NULL` values are saved with a `TextDigestField` field."""
        instance = EncryptedModel.objects.create()
        self.assertEqual(instance.integer_pgp_pub_field, None)

    def test_hmac_null(self):
        """Assert `NULL` values are saved with an `TextHMACField` field."""
        instance = EncryptedModel.objects.create()
        self.assertEqual(instance.integer_pgp_sym_field, None)

    def test_email_pgp_public_key_null(self):
        """Assert `NULL` values are saved with an `EmailPGPPublicKeyField` field."""
        instance = EncryptedModel.objects.create()
        self.assertEqual(instance.email_pgp_pub_field, None)

    def test_integer_pgp_public_key_null(self):
        """Assert `NULL` values are saved with an `IntegerPGPPublicKeyField` field."""
        instance = EncryptedModel.objects.create()
        self.assertEqual(instance.integer_pgp_pub_field, None)

    def test_text_pgp_public_key_null(self):
        """Assert `NULL` values are saved with an `TextPGPPublicKeyField` field."""
        instance = EncryptedModel.objects.create()
        self.assertEqual(instance.pgp_pub_field, None)

    def test_email_pgp_symmetric_key_null(self):
        """Assert `NULL` values are saved with an `EmailPGPSymmetricKeyField` field."""
        instance = EncryptedModel.objects.create()
        self.assertEqual(instance.email_pgp_sym_field, None)

    def test_integer_pgp_symmetric_key_null(self):
        """Assert `NULL` values are saved with an `IntegerPGPSymmetricKeyField` field."""
        instance = EncryptedModel.objects.create()
        self.assertEqual(instance.integer_pgp_sym_field, None)

    def test_text_pgp_symmetric_key_null(self):
        """Assert `NULL` values are saved with an `TextPGPSymmetricKeyField` field."""
        instance = EncryptedModel.objects.create()
        self.assertEqual(instance.pgp_sym_field, None)
