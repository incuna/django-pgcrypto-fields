class EncryptedProxyField:
    """Descriptor for encrypted values.

    Decrypted values will query the database through the field's model.

    When accessing the field name attribute on a model instance we are
    generating N+1 queries.
    """
    def __init__(self, field, raw):
        """
        Create a proxy for a django field.

        `field` is a django field.

        `raw` is an indicator defining if we need to decrypt the value.
        """
        self.field = field
        self.model = field.model
        self.aggregate = field.aggregate
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

        kwargs = {self.field.name: self.aggregate(self.field.name)}
        kw_value = self.model.objects.aggregate(**kwargs)
        return kw_value[self.field.name]

    def __set__(self, obj, value):
        """
        Setter for field's value.

        Set ensures new values are always set on the model field name
        defined.
        """
        obj.__dict__[self.field.name] = value
