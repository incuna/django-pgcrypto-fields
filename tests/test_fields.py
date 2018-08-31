from datetime import date, datetime
from unittest.mock import MagicMock

from django.test import TestCase
from incuna_test_utils.utils import field_names

from pgcrypto import aggregates, fields, proxy
from .factories import EncryptedModelFactory
from .forms import EncryptedForm
from .models import EncryptedModel, EncryptedModelWithManager

KEYED_FIELDS = (fields.TextDigestField, fields.TextHMACField)
EMAIL_PGP_FIELDS = (fields.EmailPGPPublicKeyField, fields.EmailPGPSymmetricKeyField)
PGP_FIELDS = EMAIL_PGP_FIELDS + (
    fields.DatePGPSymmetricKeyField,
    fields.DateTimePGPSymmetricKeyField,
    fields.IntegerPGPPublicKeyField,
    fields.IntegerPGPSymmetricKeyField,
    fields.TextPGPPublicKeyField,
    fields.TextPGPSymmetricKeyField,
)


class TestTextFieldHash(TestCase):
    """Test hash fields behave properly."""
    def test_get_placeholder(self):
        """Assert `get_placeholder` hash value only once."""
        for field in KEYED_FIELDS:
            with self.subTest(field=field):
                placeholder = field().get_placeholder('\\x')
                self.assertEqual(placeholder, '%s')


class TestPGPMixin(TestCase):
    """Test `PGPMixin` behave properly."""
    def test_check(self):
        """Assert `max_length` check does not return any error."""
        for field in PGP_FIELDS:
            with self.subTest(field=field):
                field.model = MagicMock()
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


class TestEmailPGPMixin(TestCase):
    """Test emails fields behave properly."""
    def test_max_length_validator(self):
        """Check `MaxLengthValidator` is not set."""
        for field in EMAIL_PGP_FIELDS:
            with self.subTest(field=field):
                field_validated = field().run_validators(value='value@value.com')
                self.assertEqual(field_validated, None)


class TestEncryptedTextFieldModel(TestCase):
    """Test `EncryptedTextField` can be integrated in a `Django` model."""
    model = EncryptedModel

    def test_fields(self):
        """Assert fields are representing our model."""
        fields = field_names(self.model)
        expected = (
            'id',
            'digest_field',
            'digest_with_original_field',
            'hmac_field',
            'hmac_with_original_field',
            'email_pgp_pub_field',
            'integer_pgp_pub_field',
            'pgp_pub_field',
            'email_pgp_sym_field',
            'integer_pgp_sym_field',
            'pgp_sym_field',
            'date_pgp_sym_field',
            'datetime_pgp_sym_field',
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

    def test_digest_with_original_lookup(self):
        """Assert we can filter a digest value."""
        value = 'bonjour'
        expected = EncryptedModelFactory.create(pgp_sym_field=value)
        EncryptedModelFactory.create()

        queryset = EncryptedModel.objects.filter(
            digest_with_original_field__hash_of=value
        )
        self.assertCountEqual(queryset, [expected])

    def test_hmac_lookup(self):
        """Assert we can filter a digest value."""
        value = 'bonjour'
        expected = EncryptedModelFactory.create(hmac_field=value)
        EncryptedModelFactory.create()

        queryset = EncryptedModel.objects.filter(hmac_field__hash_of=value)
        self.assertCountEqual(queryset, [expected])

    def test_hmac_with_original_lookup(self):
        """Assert we can filter a digest value."""
        value = 'bonjour'
        expected = EncryptedModelFactory.create(pgp_sym_field=value)
        EncryptedModelFactory.create()

        queryset = EncryptedModel.objects.filter(hmac_with_original_field__hash_of=value)
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

    def test_pgp_symmetric_key_date(self):
        """Assert date is save with an `DatePGPSymmetricKeyField` field."""
        expected = date.today()
        instance = EncryptedModelFactory.create(date_pgp_sym_field=expected)
        instance.refresh_from_db()  # Ensure the PGSQL casting works right

        self.assertEqual(instance.date_pgp_sym_field, expected)

        instance = EncryptedModel.objects.get(pk=instance.id)

        self.assertEqual(instance.date_pgp_sym_field, expected)

    def test_pgp_symmetric_key_datetime_form(self):
        """Assert form field and widget for `DateTimePGPSymmetricKeyField` field."""
        expected = datetime.now()
        instance = EncryptedModelFactory.create(date_pgp_sym_field=expected)

        payload = {
            'datetime_pgp_sym_field': '08/01/2016 14:00'
        }

        form = EncryptedForm(payload, instance=instance)
        self.assertTrue(form.is_valid())

        cleaned_data = form.cleaned_data

        self.assertTrue(
            cleaned_data['datetime_pgp_sym_field'],
            datetime(2016, 8, 1, 14, 0, 0)
        )

    def test_pgp_symmetric_key_datetime_lookups(self):
        """Assert lookups `DatePGPSymmetricKeyField` field."""
        EncryptedModelFactory.create(datetime_pgp_sym_field=datetime(2016, 7, 1, 0, 0, 0))
        EncryptedModelFactory.create(datetime_pgp_sym_field=datetime(2016, 8, 1, 0, 0, 0))
        EncryptedModelFactory.create(datetime_pgp_sym_field=datetime(2016, 9, 1, 0, 0, 0))

        # EXACT
        self.assertEqual(
            1,
            EncryptedModel.objects.filter(
                datetime_pgp_sym_field__exact=datetime(2016, 8, 1, 0, 0, 0)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                datetime_pgp_sym_field__exact=datetime(2016, 8, 1, 0, 0, 1)
            ).count()
        )

        # GT
        self.assertEqual(
            1,
            EncryptedModel.objects.filter(
                datetime_pgp_sym_field__gt=datetime(2016, 8, 1, 0, 0, 0)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                datetime_pgp_sym_field__gt=datetime(2016, 10, 1, 0, 0, 0)
            ).count()
        )

        # GTE
        self.assertEqual(
            2,
            EncryptedModel.objects.filter(
                datetime_pgp_sym_field__gte=datetime(2016, 8, 1, 0, 0, 0)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                datetime_pgp_sym_field__gte=datetime(2016, 10, 1, 0, 0, 0)
            ).count()
        )

        # LE
        self.assertEqual(
            1,
            EncryptedModel.objects.filter(
                datetime_pgp_sym_field__lt=datetime(2016, 8, 1, 0, 0, 0)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                datetime_pgp_sym_field__lt=datetime(2016, 6, 1, 0, 0, 0)
            ).count()
        )

        # LTE
        self.assertEqual(
            2,
            EncryptedModel.objects.filter(
                datetime_pgp_sym_field__lte=datetime(2016, 8, 1, 0, 0, 0)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                datetime_pgp_sym_field__lte=datetime(2016, 6, 1, 0, 0, 0)
            ).count()
        )

    def test_null(self):
        """Assert `NULL` values are saved."""
        instance = EncryptedModel.objects.create()
        fields = field_names(self.model)
        fields.remove('id')
        for field in fields:
            with self.subTest(field=field):
                self.assertEqual(getattr(instance, field), None)


class TestPGPManager(TestCase):
    """Test `PGPManager` can be integrated in a `Django` model."""
    model = EncryptedModelWithManager

    def test_auto_decryption(self):
        """Assert auto decryption via manager."""
        expected_string = 'bonjour'
        expected_date = date(2016, 9, 1)
        expected_datetime = datetime(2016, 9, 1, 0, 0, 0)

        EncryptedModelFactory.create(
            digest_field=expected_string,
            hmac_field=expected_string,
            pgp_pub_field=expected_string,
            pgp_sym_field=expected_string,
            date_pgp_sym_field=expected_date,  # Tests cast sql
            datetime_pgp_sym_field=expected_datetime,  # Tests cast sql
        )

        instance = self.model.objects.get()

        # Using `__dict__` bypasses "on the fly" decryption that normally occurs
        # if accessing a field that is not yet decrypted.
        # If decryption is not working, we get references to <In_Memory> classes
        self.assertEqual(instance.__dict__['pgp_pub_field'], expected_string)
        self.assertEqual(instance.__dict__['pgp_sym_field'], expected_string)
        self.assertEqual(instance.__dict__['date_pgp_sym_field'], expected_date)
        self.assertEqual(instance.__dict__['datetime_pgp_sym_field'], expected_datetime)

        # Ensure digest / hmac fields are unaffected
        count = self.model.objects.filter(
            digest_field__hash_of=expected_string
        ).count()
        self.assertEqual(count, 1)

        count = self.model.objects.filter(
            hmac_field__hash_of=expected_string
        ).count()
        self.assertEqual(count, 1)
