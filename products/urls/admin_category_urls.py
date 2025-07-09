from django.urls import path
from products.views import add_category, edit_category, delete_category

urlpatterns = [
    path('admin/categories/add/', add_category, name='add_category'),
    path('admin/categories/edit/<int:category_id>/', edit_category, name='admin_edit_category'),
    path('admin/categories/delete/<int:category_id>/', delete_category, name='admin_delete_category'),
]
