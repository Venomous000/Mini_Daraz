from django.urls import path
from orders.views import order_history, delete_order

urlpatterns = [
    path('orders/', order_history, name='view_orders'),
    path('orders/history/', order_history, name='order_history'),
    path('orders/delete/<int:order_id>/', delete_order, name='delete_order'),
]