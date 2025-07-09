from django.urls import path
from wishlist.views.wishlist_user_views import (
    view_wishlist,
    add_to_wishlist,
    remove_from_wishlist,
    move_to_cart,
)

urlpatterns = [
    path('', view_wishlist, name='view_wishlist'),
    path('add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('move-to-cart/<int:product_id>/', move_to_cart, name='move_to_cart'),
]
