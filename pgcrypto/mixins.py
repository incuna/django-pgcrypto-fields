from django.core.validators import MaxLengthValidator
from django.db.models.expressions import Col
from django.utils.functional import cached_property

from pgcrypto import (
    PGP_PUB_DECRYPT_SQL,
    PGP_PUB_ENCRYPT_SQL,
    PGP_SYM_DECRYPT_SQL,
    PGP_SYM_ENCRYPT_SQL,
)
from pgcrypto.forms import DateField, DateTimeField


def remove_validators(validators, validator_class):
    """Exclude `validator_class` instances from `validators` list."""
    return [v for v in validators if not isinstance(v, validator_class)]


class DecryptedCol(Col):
    """Provide DecryptedCol support without using `extra` sql."""

    def __init__(self, alias, target, output_field=None):
        """Init the decryption."""
        self.decrypt_sql = target.decrypt_sql
        self.cast_type = target.cast_type
        self.target = target

        super(DecryptedCol, self).__init__(alias, target, output_field)

    def as_sql(self, compiler, connection):
        """Build SQL with decryption and casting."""
        sql, params = super(DecryptedCol, self).as_sql(compiler, connection)
        sql = self.decrypt_sql % (sql, self.cast_type)
        return sql, params


class HashMixin:
    """Keyed hash mixin.

    `HashMixin` uses 'pgcrypto' to encrypt data in a postgres database.
    """
    encrypt_sql = None  # Set in implementation class

    def __init__(self, original=None, *args, **kwargs):
        """Tells the init the original attr."""
        self.original = original

        super(HashMixin, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        """Save the original_value."""
        if self.original:
            original_value = getattr(model_instance, self.original)
            setattr(model_instance, self.attname, original_value)

        return super(HashMixin, self).pre_save(model_instance, add)

    def get_placeholder(self, value=None, compiler=None, connection=None):
        """
        Tell postgres to encrypt this field with a hashing function.

        The `value` string is checked to determine if we need to hash or keep
        the current value.

        `compiler` and `connection` is ignored here as we don't need custom operators.
        """
        if value is None or value.startswith('\\x'):
            return '%s'
        return self.encrypt_sql


class PGPMixin:
    """PGP encryption for field's value.

    `PGPMixin` uses 'pgcrypto' to encrypt data in a postgres database.
    """
    encrypt_sql = None  # Set in implementation class
    decrypt_sql = None  # Set in implementation class
    cast_type = None

    def __init__(self, *args, **kwargs):
        """`max_length` should be set to None as encrypted text size is variable."""
        kwargs['max_length'] = None
        super().__init__(*args, **kwargs)

    def db_type(self, connection=None):
        """Value stored in the database is hexadecimal."""
        return 'bytea'

    def get_placeholder(self, value=None, compiler=None, connection=None):
        """
        Tell postgres to encrypt this field using PGP.

        `value`, `compiler`, and `connection` are ignored here as we don't need
        custom operators.
        """
        return self.encrypt_sql

    def _check_max_length_attribute(self, **kwargs):
        """Override `_check_max_length_attribute` to remove check on max_length."""
        return []

    def get_col(self, alias, output_field=None):
        """Get the decryption for col."""
        if output_field is None:
            output_field = self
        if alias != self.model._meta.db_table or output_field != self:
            return DecryptedCol(
                alias,
                self,
                output_field
            )
        else:
            return self.cached_col

    @cached_property
    def cached_col(self):
        """Get cached version of decryption for col."""
        return DecryptedCol(
            self.model._meta.db_table,
            self
        )


class PGPPublicKeyFieldMixin(PGPMixin):
    """PGP public key encrypted field mixin for postgres."""
    encrypt_sql = PGP_PUB_ENCRYPT_SQL
    decrypt_sql = PGP_PUB_DECRYPT_SQL
    cast_type = 'TEXT'


class PGPSymmetricKeyFieldMixin(PGPMixin):
    """PGP symmetric key encrypted field mixin for postgres."""
    encrypt_sql = PGP_SYM_ENCRYPT_SQL
    decrypt_sql = PGP_SYM_DECRYPT_SQL
    cast_type = 'TEXT'


class RemoveMaxLengthValidatorMixin:
    """Exclude `MaxLengthValidator` from field validators."""
    def __init__(self, *args, **kwargs):
        """Remove `MaxLengthValidator` in parent's `.__init__`."""
        super().__init__(*args, **kwargs)
        self.validators = remove_validators(self.validators, MaxLengthValidator)


class EmailPGPPublicKeyFieldMixin(PGPPublicKeyFieldMixin, RemoveMaxLengthValidatorMixin):
    """Email mixin for PGP public key fields."""


class EmailPGPSymmetricKeyFieldMixin(
    PGPSymmetricKeyFieldMixin,
    RemoveMaxLengthValidatorMixin
):
    """Email mixin for PGP symmetric key fields."""


class DatePGPPublicKeyFieldMixin(PGPPublicKeyFieldMixin):
    """Date mixin for PGP public key fields."""
    cast_type = 'DATE'

    def formfield(self, **kwargs):
        """Override the form field with custom PGP DateField."""
        defaults = {'form_class': DateField}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class DatePGPSymmetricKeyFieldMixin(PGPSymmetricKeyFieldMixin):
    """Date mixin for PGP symmetric key fields."""
    cast_type = 'DATE'

    def formfield(self, **kwargs):
        """Override the form field with custom PGP DateField."""
        defaults = {'form_class': DateField}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class DateTimePGPPublicKeyFieldMixin(PGPPublicKeyFieldMixin):
    """DateTime mixin for PGP public key fields."""
    cast_type = 'TIMESTAMP'

    def formfield(self, **kwargs):
        """Override the form field with custom PGP DateTimeField."""
        defaults = {'form_class': DateTimeField}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class DateTimePGPSymmetricKeyFieldMixin(PGPSymmetricKeyFieldMixin):
    """DateTime mixin for PGP symmetric key fields."""
    cast_type = 'TIMESTAMP'

    def formfield(self, **kwargs):
        """Override the form field with custom PGP DateTimeField."""
        defaults = {'form_class': DateTimeField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
