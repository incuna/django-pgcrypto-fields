from django import forms


class DateField(forms.DateField):
    """
    Form class for DateField.

    Removes max_length since the backend model field is a text field.
    """

    def __init__(self, input_formats=None, *args, **kwargs):
        """Init that pops off the max_length attribute."""
        kwargs.pop('max_length', None)
        super().__init__(input_formats=input_formats, **kwargs)


class DateTimeField(forms.DateTimeField):
    """
    Form class for DateTimeField.

    Remove max_length since the backend model field is a text field.
    """

    def __init__(self, input_formats=None, *args, **kwargs):
        """Init that pops off the max_length attribute."""
        kwargs.pop('max_length', None)
        super().__init__(input_formats=input_formats, **kwargs)
