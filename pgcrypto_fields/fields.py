from django.db import models

from pgcrypto_fields import aggregates


class EncryptedProxyField:
    """Descriptor for encrypted values.

    Decrypted values will query the database through the field's model.

    When accessing the field name attribute on a model instance we are
    generating N+1 query.
    """
    def __init__(self, field, raw=True):
        """
        Accept two arguments.

        `field` is a django field.

        `raw` is an indicator defining if we need to decrypt the value.
        """
        self.field = field
        self.model = field.model
        self.encryption_method = field.encryption_method
        self.raw = raw

    def __get__(self, obj, type=None):
        """
        Getter for field's value.

        Get original value when `raw` is set to `True` or when the model
        instance is not saved.

        Get the decrypted value when `raw` is False by querying the database
        with an alias set with `Decrypt`.
        """
        if not obj:
            return self

        if self.raw or not obj.pk:
            return obj.__dict__[self.field.name]

        kwargs = {self.field.name: self.encryption_method(self.field.name)}
        kw_value = self.model.objects.aggregate(**kwargs)
        return kw_value[self.field.name]

    def __set__(self, obj, value):
        """
        Setter for field's value.

        Set ensures new values are always set on the model field name
        defined.
        """
        obj.__dict__[self.field.name] = value


class TextFieldMixin:
    """Encrypted TextField.

    `TextFieldMixin` deals with postgres and use pgcrypto to encode
    data to the database. Compatible with django 1.6.x for migration.
    """
    def db_type(self, connection=None):
        """Value stored in the database is hexadecimal."""
        return 'bytea'

    def get_placeholder(self, value=None, connection=None):
        """
        Tell postgres to encrypt this field with our public pgp key.

        `value` and `connection` are ignored here as we don't need other custom
        operator depending on the value.
        """
        return self.encryption_method.encrypt_sql

    def south_field_triple(self):
        """Return a suitable description of this field for South."""
        from south.modelsinspector import introspector
        field_class = '{}.{}'.format(self.__class__.__module__, self.__class__.__name__)
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)


class EncryptedTextField(TextFieldMixin, models.TextField):
    """
    An encrypted TextField for postgres.

    `EncryptedTextField` uses pgcrypto to encrypt data in the database.
    South migrations on django 1.6.x are supported.
    """
    def __init__(self, encryption_method=aggregates.PGPPublicKey, *args, **kwargs):
        """Allow to define an encryption method."""
        super().__init__(*args, **kwargs)
        self.encryption_method = encryption_method

    def contribute_to_class(self, cls, name, **kwargs):
        """
        Add two fields on the model.

        Add to the field model an `EncryptedProxyField` to get the raw and
        decrypted values of the field.

        Raw value is accessible through `{field_name}_raw`.
        Decrypted value is accessible the usual way.
        """
        super().contribute_to_class(cls, name, **kwargs)

        raw_name = '{}_raw'.format(self.name)
        setattr(cls, self.name, EncryptedProxyField(field=self, raw=False))
        setattr(cls, raw_name, EncryptedProxyField(field=self))


class HashedTextField(TextFieldMixin, models.TextField):
    """Hashed TextField.

    `HashedTextField` deals with postgres and use pgcrypto to encode
    data to the database. Compatible with django 1.6.x for migration.
    """
    def __init__(self, encryption_method=aggregates.Digest, *args, **kwargs):
        """Allow to define an encryption method."""
        super().__init__(*args, **kwargs)
        self.encryption_method = encryption_method
