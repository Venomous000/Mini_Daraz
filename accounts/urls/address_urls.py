from django.urls import path
from accounts.views import address_views as views

urlpatterns = [
    path('', views.manage_addresses, name='manage_addresses'),
    path('add/', views.add_address, name='add_address'),
    path('edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('delete/<int:address_id>/', views.delete_address, name='delete_address'),
]
