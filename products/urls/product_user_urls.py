from django.urls import path
from products.views import user_home, product_detail

urlpatterns = [
    path('', user_home, name='home'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
]
