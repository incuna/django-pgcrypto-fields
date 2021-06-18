from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock

from django import VERSION as DJANGO_VERSION
from django.conf import settings
from django.db import connections, models, reset_queries
from django.test import TestCase
from incuna_test_utils.utils import field_names

from pgcrypto import fields
from .diff_keys.models import EncryptedDiff
from .factories import EncryptedFKModelFactory, EncryptedModelFactory
from .forms import EncryptedForm
from .models import EncryptedDateTime, EncryptedFKModel, \
    EncryptedModel, RelatedDateTime
from .password_protected.models import EncryptedPasswordProtected

KEYED_FIELDS = (fields.TextDigestField, fields.TextHMACField)
EMAIL_PGP_FIELDS = (fields.EmailPGPPublicKeyField, fields.EmailPGPSymmetricKeyField)
PGP_FIELDS = EMAIL_PGP_FIELDS + (
    fields.DatePGPSymmetricKeyField,
    fields.DateTimePGPSymmetricKeyField,
    fields.IntegerPGPPublicKeyField,
    fields.IntegerPGPSymmetricKeyField,
    fields.TextPGPPublicKeyField,
    fields.TextPGPSymmetricKeyField,
    fields.BooleanPGPPublicKeyField,
    fields.BooleanPGPSymmetricKeyField,
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
    databases = '__all__'
    """Test `PGPMixin` behave properly."""
    def test_check(self):
        """Assert `max_length` check does not return any error."""
        for field in PGP_FIELDS:
            with self.subTest(field=field):
                field.model = MagicMock()
                self.assertEqual(field(name='field').check(), [])

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
    databases = '__all__'
    """Test `EncryptedTextField` can be integrated in a `Django` model."""
    model = EncryptedModel

    # You have to do it here or queries is empty
    settings.DEBUG = True

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
            'biginteger_pgp_pub_field',
            'pgp_pub_field',
            'char_pub_field',
            'decimal_pgp_pub_field',
            'email_pgp_sym_field',
            'integer_pgp_sym_field',
            'biginteger_pgp_sym_field',
            'pgp_sym_field',
            'char_sym_field',
            'date_pgp_sym_field',
            'datetime_pgp_sym_field',
            'time_pgp_sym_field',
            'date_pgp_pub_field',
            'datetime_pgp_pub_field',
            'time_pgp_pub_field',
            'decimal_pgp_sym_field',
            'float_pgp_pub_field',
            'float_pgp_sym_field',
            'boolean_pgp_pub_field',
            'boolean_pgp_sym_field',
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
        self.assertIsInstance(instance.biginteger_pgp_pub_field, int)
        self.assertIsInstance(instance.pgp_pub_field, str)
        self.assertIsInstance(instance.date_pgp_pub_field, date)
        self.assertIsInstance(instance.datetime_pgp_pub_field, datetime)

        self.assertIsInstance(instance.email_pgp_sym_field, str)
        self.assertIsInstance(instance.integer_pgp_sym_field, int)
        self.assertIsInstance(instance.biginteger_pgp_sym_field, int)
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
        """
        Assert negative value is saved with Public Key integer fields.

        * `IntegerPGPPublicKeyField`
        * `BigIntegerPGPSymmetricKeyField`
        """
        expected = -2147483648
        instance = EncryptedModelFactory.create(integer_pgp_pub_field=expected)

        self.assertEqual(instance.integer_pgp_pub_field, expected)

        expected = -9223372036854775808
        instance = EncryptedModelFactory.create(biginteger_pgp_pub_field=expected)

        self.assertEqual(instance.biginteger_pgp_pub_field, expected)

    def test_pgp_symmetric_key_negative_number(self):
        """
        Assert negative value is saved with Symmetric Key fields.

        * `IntegerPGPSymmetricKeyField`
        * `BigIntegerPGPSymmetricKeyField`
        """
        expected = -2147483648
        instance = EncryptedModelFactory.create(integer_pgp_sym_field=expected)

        self.assertEqual(instance.integer_pgp_sym_field, expected)

        expected = -9223372036854775808
        instance = EncryptedModelFactory.create(biginteger_pgp_sym_field=expected)

        self.assertEqual(instance.biginteger_pgp_sym_field, expected)

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
        instance.refresh_from_db()  # Ensure the PGSQL casting works right

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
        instance.refresh_from_db()  # Ensure the PGSQL casting works right

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

    def test_pgp_symmetric_key_time(self):
        """Assert date is save with an `TimePGPSymmetricKeyField` field."""
        expected = datetime.now().time()
        instance = EncryptedModelFactory.create(time_pgp_sym_field=expected)
        instance.refresh_from_db()  # Ensure the PGSQL casting works right

        self.assertEqual(instance.time_pgp_sym_field, expected)

        instance = EncryptedModel.objects.get(pk=instance.id)

        self.assertEqual(instance.time_pgp_sym_field, expected)

    def test_pgp_pub_key_time(self):
        """Assert date is save with an `TimePGPPublicKeyField` field."""
        expected = datetime.now().time()
        instance = EncryptedModelFactory.create(time_pgp_pub_field=expected)
        instance.refresh_from_db()  # Ensure the PGSQL casting works right

        self.assertEqual(instance.time_pgp_pub_field, expected)

        instance = EncryptedModel.objects.get(pk=instance.id)

        self.assertEqual(instance.time_pgp_pub_field, expected)

    def test_pgp_symmetric_key_time_form(self):
        """Assert form field and widget for `TimePGPSymmetricKeyField` field."""
        expected = datetime.now().time()
        instance = EncryptedModelFactory.create(time_pgp_sym_field=expected)
        instance.refresh_from_db()  # Ensure the PGSQL casting works right

        payload = {
            'time_pgp_sym_field': '{}'.format(expected)
        }

        form = EncryptedForm(payload, instance=instance)
        self.assertTrue(form.is_valid())

        cleaned_data = form.cleaned_data

        self.assertTrue(
            cleaned_data['time_pgp_sym_field'],
            expected
        )

    def test_pgp_public_key_time_form(self):
        """Assert form field and widget for `TimePGPSymmetricKeyField` field."""
        expected = datetime.now().time()
        instance = EncryptedModelFactory.create(time_pgp_pub_field=expected)
        instance.refresh_from_db()  # Ensure the PGSQL casting works right

        payload = {
            'time_pgp_pub_field': '{}'.format(expected)
        }

        form = EncryptedForm(payload, instance=instance)
        self.assertTrue(form.is_valid())

        cleaned_data = form.cleaned_data

        self.assertTrue(
            cleaned_data['time_pgp_pub_field'],
            expected
        )

    def test_pgp_public_key_char_field(self):
        """Test public key CharField."""
        expect = 'Peter'
        EncryptedModelFactory.create(char_pub_field=expect)

        instance = EncryptedModel.objects.get()

        self.assertTrue(
            instance.char_pub_field,
            expect
        )

        payload = {
            'char_pub_field': 'This is beyond 15 max length'
        }

        form = EncryptedForm(payload, instance=instance)
        is_valid = form.is_valid()
        errors = form.errors.as_data()
        self.assertFalse(is_valid)
        self.assertTrue(1, len(errors['char_pub_field']))

    def test_pgp_symmetric_key_char_field(self):
        """Test symmetric key CharField."""
        expect = 'Peter'
        EncryptedModelFactory.create(char_sym_field=expect)

        instance = EncryptedModel.objects.get()

        self.assertTrue(
            instance.char_sym_field,
            expect
        )

        payload = {
            'char_sym_field': 'This is beyond 15 max length'
        }

        form = EncryptedForm(payload, instance=instance)
        is_valid = form.is_valid()
        errors = form.errors.as_data()
        self.assertFalse(is_valid)
        self.assertTrue(1, len(errors['char_sym_field']))

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

    def test_decimal_pgp_pub_field(self):
        """Test DecimalPGPPublicKeyField."""
        expected = '100000.99'
        EncryptedModelFactory.create(decimal_pgp_pub_field=expected)

        instance = EncryptedModel.objects.get()

        self.assertIsInstance(
            instance.decimal_pgp_pub_field,
            Decimal
        )

        self.assertEqual(
            instance.decimal_pgp_pub_field,
            Decimal(expected)
        )

        items = EncryptedModel.objects.filter(decimal_pgp_pub_field__gte='100')

        self.assertEqual(
            1,
            len(items)
        )

        items = EncryptedModel.objects.filter(decimal_pgp_pub_field__gte='100001.00')

        self.assertEqual(
            0,
            len(items)
        )

    def test_decimal_pgp_sym_field(self):
        """Test DecimalPGPSymmetricKeyField."""
        expected = '100000.99'
        EncryptedModelFactory.create(decimal_pgp_sym_field=expected)

        instance = EncryptedModel.objects.get()

        self.assertIsInstance(
            instance.decimal_pgp_sym_field,
            Decimal
        )

        self.assertEqual(
            instance.decimal_pgp_sym_field,
            Decimal(expected)
        )

        items = EncryptedModel.objects.filter(decimal_pgp_sym_field__gte='100')

        self.assertEqual(
            1,
            len(items)
        )

        items = EncryptedModel.objects.filter(decimal_pgp_sym_field__gte='100001.00')

        self.assertEqual(
            0,
            len(items)
        )

    def test_pgp_public_key_decimal_form(self):
        """Assert form field and widget for `DecimalPGPSymmetricKeyField` field."""
        expected = '100000.99'
        instance = EncryptedModelFactory.create(decimal_pgp_pub_field=expected)

        payload = {
            'decimal_pgp_pub_field': expected
        }

        form = EncryptedForm(payload, instance=instance)
        self.assertTrue(form.is_valid())

        cleaned_data = form.cleaned_data

        self.assertTrue(
            cleaned_data['decimal_pgp_pub_field'],
            Decimal(expected)
        )

    def test_pgp_symmetric_key_decimal_form(self):
        """Assert form field and widget for `DecimalPGPSymmetricKeyField` field."""
        expected = '100000.99'
        instance = EncryptedModelFactory.create(decimal_pgp_sym_field=expected)

        payload = {
            'decimal_pgp_sym_field': expected
        }

        form = EncryptedForm(payload, instance=instance)
        self.assertTrue(form.is_valid())

        cleaned_data = form.cleaned_data

        self.assertTrue(
            cleaned_data['decimal_pgp_sym_field'],
            Decimal(expected)
        )

    def test_float_pgp_pub_field(self):
        """Test FloatPGPPublicKeyField."""
        expected = 1234.6788
        EncryptedModelFactory.create(float_pgp_pub_field=expected)

        instance = EncryptedModel.objects.get()

        self.assertIsInstance(
            instance.float_pgp_pub_field,
            float
        )

        self.assertEqual(
            instance.float_pgp_pub_field,
            expected
        )

        items = EncryptedModel.objects.filter(float_pgp_pub_field__gte='100')

        self.assertEqual(
            1,
            len(items)
        )

        items = EncryptedModel.objects.filter(float_pgp_pub_field__gte='100001.00')

        self.assertEqual(
            0,
            len(items)
        )

    def test_float_pgp_sym_field(self):
        """Test FloatPGPSymmetricKeyField."""
        expected = float(1234.6788)
        EncryptedModelFactory.create(float_pgp_sym_field=expected)

        instance = EncryptedModel.objects.get()

        self.assertIsInstance(
            instance.float_pgp_sym_field,
            float
        )

        self.assertEqual(
            instance.float_pgp_sym_field,
            expected
        )

        items = EncryptedModel.objects.filter(float_pgp_sym_field__gte='100')

        self.assertEqual(
            1,
            len(items)
        )

        items = EncryptedModel.objects.filter(float_pgp_sym_field__gte='100001.00')

        self.assertEqual(
            0,
            len(items)
        )

    def test_pgp_public_key_float_form(self):
        """Assert form field and widget for `FloatPGPPublicKeyField` field."""
        expected = '100000.99'
        instance = EncryptedModelFactory.create(float_pgp_pub_field=expected)

        payload = {
            'float_pgp_pub_field': expected
        }

        form = EncryptedForm(payload, instance=instance)
        self.assertTrue(form.is_valid())

        cleaned_data = form.cleaned_data

        self.assertTrue(
            cleaned_data['float_pgp_pub_field'],
            float(expected)
        )

    def test_pgp_symmetric_key_float_form(self):
        """Assert form field and widget for `FloatPGPSymmetricKeyField` field."""
        expected = '100000.99'
        instance = EncryptedModelFactory.create(float_pgp_sym_field=expected)

        payload = {
            'float_pgp_sym_field': expected
        }

        form = EncryptedForm(payload, instance=instance)
        self.assertTrue(form.is_valid())

        cleaned_data = form.cleaned_data

        self.assertTrue(
            cleaned_data['float_pgp_sym_field'],
            float(expected)
        )

    def test_boolean_pgp_pub_field(self):
        """Test BooleanPGPPublicKeyField."""
        expected = True
        EncryptedModelFactory.create(boolean_pgp_pub_field=expected)

        instance = EncryptedModel.objects.get()

        self.assertIsInstance(
            instance.boolean_pgp_pub_field,
            bool
        )

        self.assertEqual(
            instance.boolean_pgp_pub_field,
            expected
        )

        items = EncryptedModel.objects.filter(boolean_pgp_pub_field=True)

        self.assertEqual(
            1,
            len(items)
        )

        items = EncryptedModel.objects.filter(boolean_pgp_pub_field=False)

        self.assertEqual(
            0,
            len(items)
        )

    def test_boolean_pgp_sym_field(self):
        """Test BooleanPGPSymmetricKeyField."""
        expected = False
        EncryptedModelFactory.create(boolean_pgp_sym_field=expected)

        instance = EncryptedModel.objects.get()

        self.assertIsInstance(
            instance.boolean_pgp_sym_field,
            bool
        )

        self.assertEqual(
            instance.boolean_pgp_sym_field,
            expected
        )

        items = EncryptedModel.objects.filter(boolean_pgp_sym_field=False)

        self.assertEqual(
            1,
            len(items)
        )

        items = EncryptedModel.objects.filter(float_pgp_sym_field=True)

        self.assertEqual(
            0,
            len(items)
        )

    def test_pgp_public_key_boolean_form(self):
        """Assert form field and widget for `BooleanPGPPublicKeyField` field."""
        expected = False
        instance = EncryptedModelFactory.create(boolean_pgp_pub_field=expected)

        payload = {
            'boolean_pgp_pub_field': expected
        }

        form = EncryptedForm(payload, instance=instance)
        self.assertTrue(form.is_valid())

        cleaned_data = form.cleaned_data

        self.assertEqual(
            cleaned_data['boolean_pgp_pub_field'],
            expected
        )

    def test_pgp_symmetric_key_boolean_form(self):
        """Assert form field and widget for `BooleanPGPSymmetricKeyField` field."""
        expected = True
        instance = EncryptedModelFactory.create(boolean_pgp_sym_field=expected)

        payload = {
            'boolean_pgp_sym_field': expected
        }

        form = EncryptedForm(payload, instance=instance)
        self.assertTrue(form.is_valid())

        cleaned_data = form.cleaned_data

        self.assertEqual(
            cleaned_data['boolean_pgp_sym_field'],
            expected
        )

    def test_null(self):
        """Assert `NULL` values are saved."""
        instance = EncryptedModel.objects.create()
        fields = field_names(self.model)
        fields.remove('id')

        for field in fields:
            with self.subTest(instance=instance, field=field):
                value = getattr(instance, field)
                self.assertEqual(
                    value,
                    None,
                    msg='Field {}, Value: {}'.format(field, value)
                )

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
        """Test only() functionality."""
        expected = 'bonjour'
        EncryptedModelFactory.create(pgp_sym_field=expected, pgp_pub_field=expected)
        instance = self.model.objects.only('pgp_sym_field').get()

        # Assert that accessing a field in only() does not cause a query
        with self.assertNumQueries(0):
            temp = instance.pgp_sym_field

        self.assertEqual(temp, expected)

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

    def test_aggregates(self):
        """Test aggregate support."""
        EncryptedModelFactory.create(datetime_pgp_sym_field=datetime(2016, 7, 1, 0, 0, 0))
        EncryptedModelFactory.create(datetime_pgp_sym_field=datetime(2016, 7, 2, 0, 0, 0))
        EncryptedModelFactory.create(datetime_pgp_sym_field=datetime(2016, 8, 1, 0, 0, 0))
        EncryptedModelFactory.create(datetime_pgp_sym_field=datetime(2016, 9, 1, 0, 0, 0))
        EncryptedModelFactory.create(datetime_pgp_sym_field=datetime(2016, 9, 2, 0, 0, 0))

        total_2016 = self.model.objects.aggregate(
            count=models.Count('datetime_pgp_sym_field')
        )

        self.assertEqual(5, total_2016['count'])

        total_july = self.model.objects.filter(
            datetime_pgp_sym_field__range=[
                datetime(2016, 7, 1, 0, 0, 0),
                datetime(2016, 7, 30, 23, 59, 59)
            ]
        ).aggregate(
            count=models.Count('datetime_pgp_sym_field')
        )

        self.assertEqual(2, total_july['count'])

        total_2016 = self.model.objects.aggregate(
            count=models.Count('datetime_pgp_sym_field'),
            min=models.Min('datetime_pgp_sym_field'),
            max=models.Max('datetime_pgp_sym_field'),
        )

        self.assertEqual(5, total_2016['count'])
        self.assertEqual(datetime(2016, 7, 1, 0, 0, 0), total_2016['min'])
        self.assertEqual(datetime(2016, 9, 2, 0, 0, 0), total_2016['max'])

        total_july = self.model.objects.filter(
            datetime_pgp_sym_field__range=[
                datetime(2016, 7, 1, 0, 0, 0),
                datetime(2016, 7, 30, 23, 59, 59)
            ]
        ).aggregate(
            count=models.Count('datetime_pgp_sym_field'),
            min=models.Min('datetime_pgp_sym_field'),
            max=models.Max('datetime_pgp_sym_field'),
        )

        self.assertEqual(2, total_july['count'])
        self.assertEqual(datetime(2016, 7, 1, 0, 0, 0), total_july['min'])
        self.assertEqual(datetime(2016, 7, 2, 0, 0, 0), total_july['max'])

    def test_distinct(self):
        """Test distinct support."""
        EncryptedModelFactory.create(pgp_sym_field='Paul')
        EncryptedModelFactory.create(pgp_sym_field='Paul')
        EncryptedModelFactory.create(pgp_sym_field='Peter')
        EncryptedModelFactory.create(pgp_sym_field='Peter')
        EncryptedModelFactory.create(pgp_sym_field='Jessica')
        EncryptedModelFactory.create(pgp_sym_field='Jessica')

        items = self.model.objects.filter(
            pgp_sym_field__startswith='P'
        ).annotate(
            _distinct=models.F('pgp_sym_field')
        ).only(
            'id', 'pgp_sym_field', 'fk_model__fk_pgp_sym_field'
        ).distinct(
            '_distinct'
        )

        self.assertEqual(
            2,
            len(items)
        )

        # This only works on Django 2.1+
        if DJANGO_VERSION[0] >= 2 and DJANGO_VERSION[1] >= 1:
            items = self.model.objects.filter(
                pgp_sym_field__startswith='P'
            ).only(
                'id', 'pgp_sym_field', 'fk_model__fk_pgp_sym_field'
            ).distinct(
                'pgp_sym_field'
            )

            self.assertEqual(
                2,
                len(items)
            )

    def test_annotate(self):
        """Test annotate support."""
        efk = EncryptedFKModelFactory.create()
        EncryptedModelFactory.create(pgp_sym_field='Paul', fk_model=efk)
        EncryptedModelFactory.create(pgp_sym_field='Peter', fk_model=efk)
        EncryptedModelFactory.create(pgp_sym_field='Peter', fk_model=efk)
        EncryptedModelFactory.create(pgp_sym_field='Jessica', fk_model=efk)

        items = EncryptedFKModel.objects.annotate(
            name_count=models.Count('encryptedmodel')
        )

        self.assertEqual(
            4,
            items[0].name_count
        )

        items = EncryptedFKModel.objects.filter(
            encryptedmodel__pgp_sym_field__startswith='J'
        ).annotate(
            name_count=models.Count('encryptedmodel')
        )

        self.assertEqual(
            1,
            items[0].name_count
        )

    def test_get_col(self):
        """Test get_col for related alias."""
        related = EncryptedDateTime.objects.create(value=datetime.now())
        related_again = EncryptedDateTime.objects.create(value=datetime.now())

        RelatedDateTime.objects.create(related=related, related_again=related_again)

        instance = RelatedDateTime.objects.select_related(
            'related', 'related_again'
        ).get()

        self.assertIsInstance(instance, RelatedDateTime)

    def test_char_field_choices(self):
        """Test CharField choices."""
        expected = 1
        instance = EncryptedDiff.objects.create(
            pub_field=expected,
            sym_field=expected,
        )
        instance.refresh_from_db()

        # choices always come back as strings
        self.assertTrue(
            '{}'.format(expected),
            instance.pub_field
        )

        self.assertTrue(
            '{}'.format(expected),
            instance.sym_field
        )

    def test_write_to_diff_keys(self):
        """Test writing to diff_keys db which uses different keys."""
        expected = 'a'
        instance = EncryptedDiff.objects.create(
            pub_field=expected,
            sym_field=expected,
            digest_field=expected,
            hmac_field=expected,
        )

        reset_queries()  # Required for Django 1.11
        instance = EncryptedDiff.objects.get()

        self.assertTrue(
            instance.pub_field,
            expected
        )
        self.assertTrue(
            instance.sym_field,
            expected
        )

        conn = connections['diff_keys']
        query = conn.queries[0]

        self.assertIn(
            'djangorocks',
            str(query)
        )

        self.assertIn(
            'lQNTBFvGJCARCAD',
            str(query)
        )

        instance = EncryptedDiff.objects.get(digest_field__hash_of=expected)

        self.assertTrue(
            instance.digest_field,
            expected
        )

        instance = EncryptedDiff.objects.get(hmac_field__hash_of=expected)

        self.assertTrue(
            instance.hmac_field,
            expected
        )

    def test_write_to_password_protected(self):
        """Test writing to password_protected db which uses a password-protected keys."""
        expected = 'test value'
        instance = EncryptedPasswordProtected.objects.create(pub_field=expected)
        instance.refresh_from_db()
        self.assertTrue(
            instance.pub_field,
            expected
        )
