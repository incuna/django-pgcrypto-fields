from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super

from django import forms
from future import standard_library


standard_library.install_aliases()


class DateField(forms.DateField):
    """
    Form class for DateField.

    Removes max_length since the backend model field is a text field.
    """

    def __init__(self, input_formats=None, *args, **kwargs):
        """Init that pops off the max_length attribute."""
        kwargs.pop('max_length', None)
        super(DateField, self).__init__(input_formats, *args, **kwargs)


class DateTimeField(forms.DateTimeField):
    """
    Form class for DateTimeField.

    Remove max_length since the backend model field is a text field.
    """

    def __init__(self, input_formats=None, *args, **kwargs):
        """Init that pops off the max_length attribute."""
        kwargs.pop('max_length', None)
        super(DateTimeField, self).__init__(input_formats, *args, **kwargs)
