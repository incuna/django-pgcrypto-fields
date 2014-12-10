class EncryptedProxyField:
    """Descriptor for encrypted values.

    Decrypted values will query the database through the field's model.

    When accessing the field name attribute on a model instance we are
    generating N+1 queries.
    """
    def __init__(self, field):
        """
        Create a proxy for a django field.

        `field` is a django field.
        """
        self.field = field
        self.model = field.model
        self.aggregate = field.aggregate

    def __get__(self, instance, owner=None):
        """
        Retrieve the value of the field from the instance.

        If the value has been saved to the database, decrypt it using an aggregate query.
        """
        if not instance:
            return self

        if not instance.pk:
            return instance.__dict__[self.field.name]

        # Value assigned from `__set__`
        value = instance.__dict__[self.field.name]

        if isinstance(value, str):
            return value

        if isinstance(value, memoryview):
            kwargs = {self.field.name: self.aggregate(self.field.name)}
            kw_value = self.model.objects.filter(pk=instance.pk).aggregate(**kwargs)
            instance.__dict__[self.field.name] = kw_value[self.field.name]

        return instance.__dict__[self.field.name]

    def __set__(self, instance, value):
        """
        Store a value in the model instance's __dict__.

        The value will be keyed by the field's name.
        """
        instance.__dict__[self.field.name] = value
