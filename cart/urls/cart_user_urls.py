from django.urls import path
from cart.views import (
    view_cart,
    add_to_cart,
    remove_from_cart,
    update_cart_item,
)

urlpatterns = [
    path('', view_cart, name='view_cart'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'),
    path('update/<int:cart_item_id>/', update_cart_item, name='update_cart_item'),
]
