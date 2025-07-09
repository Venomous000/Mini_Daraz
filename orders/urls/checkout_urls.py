from django.urls import path
from orders.views import guest_checkout_views
from orders.views import (
    cart_checkout, place_cart_order,
    buy_now, checkout_buy_now, place_buy_now_order,
)

urlpatterns = [
    path('checkout/cart/', cart_checkout, name='cart_checkout'),
    path('checkout/cart/place/', place_cart_order, name='place_cart_order'),

    path('checkout/buy-now/<int:product_id>/', buy_now, name='buy_now'),
    path('checkout/buy-now/', checkout_buy_now, name='checkout_buy_now'),
    path('checkout/buy-now/place/', place_buy_now_order, name='place_buy_now_order'),

    path('guest/cart/checkout/', guest_checkout_views.guest_cart_checkout, name='guest_cart_checkout'),
    path('guest/cart/place/', guest_checkout_views.place_cart_order_guest, name='place_cart_order_guest'),
    path('guest-buy-now/<int:product_id>/', guest_checkout_views.guest_buy_now, name='guest_buy_now'),
    path('guest-checkout/', guest_checkout_views.guest_checkout_view, name='guest_checkout'),
    path('guest-success/', guest_checkout_views.guest_order_success, name='guest_order_success'),
    path('buy-now-entry/<int:product_id>/', guest_checkout_views.buy_now_entry_point, name='buy_now_entry_point'),
]
