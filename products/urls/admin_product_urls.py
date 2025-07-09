from django.urls import path
from products.views import (
    admin_product_list,
    add_product,
    edit_product,
    delete_product,
    upload_product_image,
    delete_product_image,
)

urlpatterns = [
    path('admin/products/', admin_product_list, name='admin_product_list'),
    path('admin/products/add/', add_product, name='add_product'),
    path('admin/products/edit/<int:product_id>/', edit_product, name='edit_product'),
    path('admin/products/delete/<int:product_id>/', delete_product, name='delete_product'),
    path('admin/products/<int:product_id>/upload-image/', upload_product_image, name='upload_product_image'),
    path('admin/products/delete-image/<int:image_id>/', delete_product_image, name='admin_delete_product_image'),
]
