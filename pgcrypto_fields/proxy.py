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

    def __get__(self, obj, type=None):
        """
        Getter for field's value.

        Get the decrypted value by querying the database with an alias set with
        an aggregate class.
        """
        if not obj:
            return self

        if not obj.pk:
            return obj.__dict__[self.field.name]

        kwargs = {self.field.name: self.aggregate(self.field.name)}
        kw_value = self.model.objects.filter(pk=obj.pk).aggregate(**kwargs)
        return kw_value[self.field.name]
