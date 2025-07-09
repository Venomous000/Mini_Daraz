from django.urls import path, include

urlpatterns = [
    path('', include('accounts.urls.user_urls')),
    path('addresses/', include('accounts.urls.address_urls')),
    path('superadmin/', include('accounts.urls.admin_urls')),
]