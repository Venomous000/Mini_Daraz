from .order_user_urls import urlpatterns as order_user_urls
from .checkout_urls import urlpatterns as checkout_urls
from .order_admin_urls import urlpatterns as order_admin_urls
from orders.views import (
    buy_now,
    checkout_buy_now,
    place_buy_now_order,
    cart_checkout,
    place_cart_order,
    guest_cart_checkout,
)
urlpatterns = order_user_urls + checkout_urls + order_admin_urls 
