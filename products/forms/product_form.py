from django import forms
from products.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'product_name',
            'category',
            'stock_quantity',
            'price_per_piece',
            'product_description',
            'is_active'
        ]
