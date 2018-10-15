from django import forms

from .models import EncryptedModel


class EncryptedForm(forms.ModelForm):
    """Test for EncryptedModel."""
    class Meta:
        """Meta for form."""
        model = EncryptedModel
        fields = '__all__'
        widgets = {
            'date_pgp_sym_field': forms.DateInput(format='%m/%d/%Y'),
            'datetime_pgp_sym_field': forms.DateTimeInput(format='%m/%d/%Y %I:%M'),
            'date_pgp_pub_field': forms.DateInput(format='%m/%d/%Y'),
            'datetime_pgp_pub_field': forms.DateTimeInput(format='%m/%d/%Y %I:%M'),
            'decimal_pgp_pub_field': forms.NumberInput(),
            'decimal_pgp_sym_field': forms.NumberInput(),
        }
