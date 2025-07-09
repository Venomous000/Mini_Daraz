from django.urls import path
from orders.views import admin_order_list, admin_order_detail

urlpatterns = [
    path('admin/orders/', admin_order_list, name='admin_order_list'),
    path('admin/orders/<int:order_id>/', admin_order_detail, name='admin_order_detail'),
]
