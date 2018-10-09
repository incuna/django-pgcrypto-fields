from datetime import date, datetime
from unittest.mock import MagicMock

from django.test import TestCase
from incuna_test_utils.utils import field_names

from pgcrypto import fields
from .factories import EncryptedModelFactory
from .forms import EncryptedForm
from .models import EncryptedModel

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
            'date_pgp_pub_field',
            'datetime_pgp_pub_field',
            'fk_model',
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
        self.assertIsInstance(instance.date_pgp_pub_field, date)
        self.assertIsInstance(instance.datetime_pgp_pub_field, datetime)

        self.assertIsInstance(instance.email_pgp_sym_field, str)
        self.assertIsInstance(instance.integer_pgp_sym_field, int)
        self.assertIsInstance(instance.pgp_sym_field, str)
        self.assertIsInstance(instance.date_pgp_sym_field, date)
        self.assertIsInstance(instance.datetime_pgp_sym_field, datetime)

    def test_value_query(self):
        """Assert querying the field's value is making zero queries."""
        expected = 'bonjour'
        temp = None
        EncryptedModelFactory.create(pgp_pub_field=expected)

        instance = self.model.objects.get()

        with self.assertNumQueries(0):
            temp = instance.pgp_pub_field

        self.assertEqual(expected, temp)

    def test_value_pgp_pub(self):
        """Assert we can get back the decrypted value."""
        expected = 'bonjour'
        EncryptedModelFactory.create(pgp_pub_field=expected)

        instance = self.model.objects.get()
        value = instance.pgp_pub_field

        self.assertEqual(value, expected)

    def test_value_pgp_pub_multiple(self):
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

    def test_decrypt_filter(self):
        """Assert we can get filter the decrypted value."""
        expected = 'bonjour'
        EncryptedModelFactory.create(
            pgp_pub_field=expected,
        )

        queryset = self.model.objects.filter(
            copy_pgp_pub_field=expected
        )

        instance = queryset.first()
        self.assertEqual(instance.copy_pgp_pub_field, expected)

        queryset = self.model.objects.filter(
            pgp_pub_field=expected
        )

        instance = queryset.first()
        self.assertEqual(instance.pgp_pub_field, expected)

        queryset = self.model.objects.filter(
            pgp_pub_field__contains='jour'
        )

        instance = queryset.first()
        self.assertEqual(instance.pgp_pub_field, expected)

        queryset = self.model.objects.filter(
            pgp_pub_field__startswith='bon'
        )

        instance = queryset.first()
        self.assertEqual(instance.pgp_pub_field, expected)

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

    def test_pgp_pub_key_date(self):
        """Assert date is save with an `DatePGPPublicKeyField` field."""
        expected = date.today()
        instance = EncryptedModelFactory.create(date_pgp_pub_field=expected)
        instance.refresh_from_db()  # Ensure the PGSQL casting works right

        self.assertEqual(instance.date_pgp_pub_field, expected)

        instance = EncryptedModel.objects.get(pk=instance.id)

        self.assertEqual(instance.date_pgp_pub_field, expected)

    def test_pgp_symmetric_key_date_form(self):
        """Assert form field and widget for `DateTimePGPSymmetricKeyField` field."""
        expected = date.today()
        instance = EncryptedModelFactory.create(date_pgp_sym_field=expected)

        payload = {
            'date_pgp_sym_field': '08/01/2016'
        }

        form = EncryptedForm(payload, instance=instance)
        self.assertTrue(form.is_valid())

        cleaned_data = form.cleaned_data

        self.assertTrue(
            cleaned_data['date_pgp_sym_field'],
            date(2016, 8, 1)
        )

    def test_pgp_symmetric_key_datetime_form(self):
        """Assert form field and widget for `DateTimePGPSymmetricKeyField` field."""
        expected = datetime.now()
        instance = EncryptedModelFactory.create(datetime_pgp_sym_field=expected)

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

    def test_pgp_symmetric_key_date_lookups(self):
        """Assert lookups `DatePGPSymmetricKeyField` field."""
        EncryptedModelFactory.create(date_pgp_sym_field=date(2016, 7, 1))
        EncryptedModelFactory.create(date_pgp_sym_field=date(2016, 8, 1))
        EncryptedModelFactory.create(date_pgp_sym_field=date(2016, 9, 1))

        # EXACT
        self.assertEqual(
            1,
            EncryptedModel.objects.filter(
                date_pgp_sym_field__exact=date(2016, 8, 1)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                date_pgp_sym_field__exact=date(2016, 8, 2)
            ).count()
        )

        # GT
        self.assertEqual(
            1,
            EncryptedModel.objects.filter(
                date_pgp_sym_field__gt=date(2016, 8, 1)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                date_pgp_sym_field__gt=date(2016, 10, 1)
            ).count()
        )

        # GTE
        self.assertEqual(
            2,
            EncryptedModel.objects.filter(
                date_pgp_sym_field__gte=date(2016, 8, 1)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                date_pgp_sym_field__gte=date(2016, 10, 1)
            ).count()
        )

        # LE
        self.assertEqual(
            1,
            EncryptedModel.objects.filter(
                date_pgp_sym_field__lt=date(2016, 8, 1)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                date_pgp_sym_field__lt=date(2016, 6, 1)
            ).count()
        )

        # LTE
        self.assertEqual(
            2,
            EncryptedModel.objects.filter(
                date_pgp_sym_field__lte=date(2016, 8, 1)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                date_pgp_sym_field__lte=date(2016, 6, 1)
            ).count()
        )

        # RANGE
        self.assertEqual(
            3,
            EncryptedModel.objects.filter(
                date_pgp_sym_field__range=[date(2016, 6, 1), date(2016, 11, 1)]
            ).count()
        )

        self.assertEqual(
            2,
            EncryptedModel.objects.filter(
                date_pgp_sym_field__range=[date(2016, 7, 1), date(2016, 8, 1)]
            ).count()
        )

        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                date_pgp_sym_field__range=[date(2016, 10, 2), None]
            ).count()
        )

    def test_pgp_pub_key_date_lookups(self):
        """Assert lookups `DatePGPPublicKeyField` field."""
        EncryptedModelFactory.create(date_pgp_pub_field=date(2016, 7, 1))
        EncryptedModelFactory.create(date_pgp_pub_field=date(2016, 8, 1))
        EncryptedModelFactory.create(date_pgp_pub_field=date(2016, 9, 1))

        # EXACT
        self.assertEqual(
            1,
            EncryptedModel.objects.filter(
                date_pgp_pub_field__exact=date(2016, 8, 1)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                date_pgp_pub_field__exact=date(2016, 8, 2)
            ).count()
        )

        # GT
        self.assertEqual(
            1,
            EncryptedModel.objects.filter(
                date_pgp_pub_field__gt=date(2016, 8, 1)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                date_pgp_pub_field__gt=date(2016, 10, 1)
            ).count()
        )

        # GTE
        self.assertEqual(
            2,
            EncryptedModel.objects.filter(
                date_pgp_pub_field__gte=date(2016, 8, 1)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                date_pgp_pub_field__gte=date(2016, 10, 1)
            ).count()
        )

        # LE
        self.assertEqual(
            1,
            EncryptedModel.objects.filter(
                date_pgp_pub_field__lt=date(2016, 8, 1)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                date_pgp_pub_field__lt=date(2016, 6, 1)
            ).count()
        )

        # LTE
        self.assertEqual(
            2,
            EncryptedModel.objects.filter(
                date_pgp_pub_field__lte=date(2016, 8, 1)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                date_pgp_pub_field__lte=date(2016, 6, 1)
            ).count()
        )

        # RANGE
        self.assertEqual(
            3,
            EncryptedModel.objects.filter(
                date_pgp_pub_field__range=[date(2016, 6, 1), date(2016, 11, 1)]
            ).count()
        )

        self.assertEqual(
            2,
            EncryptedModel.objects.filter(
                date_pgp_pub_field__range=[date(2016, 7, 1), date(2016, 8, 1)]
            ).count()
        )

        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                date_pgp_pub_field__range=[date(2016, 10, 2), None]
            ).count()
        )

    def test_pgp_symmetric_key_datetime_lookups(self):
        """Assert lookups `DateTimePGPSymmetricKeyField` field."""
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

        # RANGE
        self.assertEqual(
            3,
            EncryptedModel.objects.filter(
                datetime_pgp_sym_field__range=[
                    datetime(2016, 6, 1, 0, 0, 0),
                    datetime(2016, 11, 1, 23, 59, 59)
                ]
            ).count()
        )

        self.assertEqual(
            2,
            EncryptedModel.objects.filter(
                datetime_pgp_sym_field__range=[
                    datetime(2016, 7, 1, 0, 0, 0),
                    datetime(2016, 8, 1, 0, 0, 0)
                ]
            ).count()
        )

        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                datetime_pgp_sym_field__range=[
                    datetime(2016, 10, 1, 0, 0, 1),
                    None
                ]
            ).count()
        )

    def test_pgp_public_key_datetime_lookups(self):
        """Assert lookups `DateTimePGPPublicKeyField` field."""
        EncryptedModelFactory.create(datetime_pgp_pub_field=datetime(2016, 7, 1, 0, 0, 0))
        EncryptedModelFactory.create(datetime_pgp_pub_field=datetime(2016, 8, 1, 0, 0, 0))
        EncryptedModelFactory.create(datetime_pgp_pub_field=datetime(2016, 9, 1, 0, 0, 0))

        # EXACT
        self.assertEqual(
            1,
            EncryptedModel.objects.filter(
                datetime_pgp_pub_field__exact=datetime(2016, 8, 1, 0, 0, 0)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                datetime_pgp_pub_field__exact=datetime(2016, 8, 1, 0, 0, 1)
            ).count()
        )

        # GT
        self.assertEqual(
            1,
            EncryptedModel.objects.filter(
                datetime_pgp_pub_field__gt=datetime(2016, 8, 1, 0, 0, 0)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                datetime_pgp_pub_field__gt=datetime(2016, 10, 1, 0, 0, 0)
            ).count()
        )

        # GTE
        self.assertEqual(
            2,
            EncryptedModel.objects.filter(
                datetime_pgp_pub_field__gte=datetime(2016, 8, 1, 0, 0, 0)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                datetime_pgp_pub_field__gte=datetime(2016, 10, 1, 0, 0, 0)
            ).count()
        )

        # LE
        self.assertEqual(
            1,
            EncryptedModel.objects.filter(
                datetime_pgp_pub_field__lt=datetime(2016, 8, 1, 0, 0, 0)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                datetime_pgp_pub_field__lt=datetime(2016, 6, 1, 0, 0, 0)
            ).count()
        )

        # LTE
        self.assertEqual(
            2,
            EncryptedModel.objects.filter(
                datetime_pgp_pub_field__lte=datetime(2016, 8, 1, 0, 0, 0)
            ).count()
        )
        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                datetime_pgp_pub_field__lte=datetime(2016, 6, 1, 0, 0, 0)
            ).count()
        )

        # RANGE
        self.assertEqual(
            3,
            EncryptedModel.objects.filter(
                datetime_pgp_pub_field__range=[
                    datetime(2016, 6, 1, 0, 0, 0),
                    datetime(2016, 11, 1, 23, 59, 59)
                ]
            ).count()
        )

        self.assertEqual(
            2,
            EncryptedModel.objects.filter(
                datetime_pgp_pub_field__range=[
                    datetime(2016, 7, 1, 0, 0, 0),
                    datetime(2016, 8, 1, 0, 0, 0)
                ]
            ).count()
        )

        self.assertEqual(
            0,
            EncryptedModel.objects.filter(
                datetime_pgp_pub_field__range=[
                    datetime(2016, 10, 1, 0, 0, 1),
                    None
                ]
            ).count()
        )

    def test_null(self):
        """Assert `NULL` values are saved."""
        instance = EncryptedModelFactory.create()
        fields = field_names(self.model)
        fields.remove('id')
        for field in fields:
            with self.subTest(field=field):
                self.assertNotEqual(getattr(instance, field), None)

    def test_defer(self):
        """Test defer() functionality."""
        expected = 'bonjour'
        EncryptedModelFactory.create(pgp_sym_field=expected)
        instance = self.model.objects.defer('pgp_sym_field').get()

        # Assert that accessing a field that is in defer() causes a query
        with self.assertNumQueries(1):
            temp = instance.pgp_sym_field

        self.assertEqual(temp, expected)

    def test_only(self):
        """Test defer() functionality."""
        expected = 'bonjour'
        EncryptedModelFactory.create(pgp_sym_field=expected, pgp_pub_field=expected)
        instance = self.model.objects.only('pgp_sym_field').get()

        # Assert that accessing a field not in only() causes a query
        with self.assertNumQueries(1):
            temp = instance.pgp_pub_field

        self.assertEqual(temp, expected)

    def test_fk_auto_decryption(self):
        """Test auto decryption of FK when select related is defined."""
        expected = 'bonjour'
        EncryptedModelFactory.create(fk_model__fk_pgp_sym_field=expected)
        instance = self.model.objects.select_related('fk_model').get()

        # Assert no additional queries are made to decrypt
        with self.assertNumQueries(0):
            temp = instance.fk_model.fk_pgp_sym_field

        self.assertEqual(temp, expected)

    def test_get_by_natural_key(self):
        """Test get_by_natual_key() support."""
        expected = 'peter@test.com'
        EncryptedModelFactory.create(email_pgp_pub_field=expected)

        instance = self.model.objects.get_by_natural_key(expected)

        self.assertEqual(instance.email_pgp_pub_field, expected)

    def test_get_or_create(self):
        """Test get_or_create() support."""
        expected = 'peter@test.com'
        original = EncryptedModelFactory.create(email_pgp_pub_field=expected)

        instance, created = self.model.objects.get_or_create(
            email_pgp_pub_field=expected
        )

        self.assertFalse(created)
        self.assertEqual(instance.id, original.id)
        self.assertEqual(instance.email_pgp_pub_field, original.email_pgp_pub_field)

        instance, created = self.model.objects.get_or_create(
            email_pgp_pub_field='jessica@test.com'
        )

        self.assertTrue(created)
        self.assertNotEqual(instance.id, original.id)
        self.assertEqual(instance.email_pgp_pub_field, 'jessica@test.com')

    def test_update_or_create(self):
        """Test update_or_create() support."""
        expected = 'peter@test.com'
        original = EncryptedModelFactory.create(
            email_pgp_pub_field=expected,
            pgp_sym_field='Test'
        )

        instance, created = self.model.objects.update_or_create(
            email_pgp_pub_field='jessica@test.com'
        )

        self.assertTrue(created)
        self.assertNotEqual(instance.id, original.id)
        self.assertEqual(instance.email_pgp_pub_field, 'jessica@test.com')

        instance, created = self.model.objects.update_or_create(
            email_pgp_pub_field='jessica@test.com',
            defaults={
                'pgp_sym_field': 'Blue',
            }
        )

        self.assertFalse(created)
        self.assertNotEqual(instance.id, original.id)
        self.assertEqual(instance.pgp_sym_field, 'Blue')
