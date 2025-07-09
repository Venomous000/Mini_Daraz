from django.urls import path
from accounts.views import admin_views as views

urlpatterns = [
    path('superadmin/login/', views.superadmin_login_view, name='superadmin_login'),
    path('superadmin/logout/', views.superadmin_logout_view, name='superadmin_logout'),
    path('superadmin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
