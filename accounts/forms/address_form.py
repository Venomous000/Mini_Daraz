from django import forms
from accounts.models.address_model import Address


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'full_name',
            'phone',
            'street_address',
            'zip_code',
            'city',
            'province',
            'country',
            'is_default',
        ]
        widgets = {
            'street_address': forms.Textarea(attrs={'rows': 2}),
        }
