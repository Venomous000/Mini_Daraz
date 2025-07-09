from django import forms
from products.models import ProductImage


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
        labels = {'image': 'Product Image'}
