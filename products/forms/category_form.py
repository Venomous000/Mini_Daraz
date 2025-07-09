from django import forms
from products.models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {'name': 'Category Name'}
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            })
        }
        