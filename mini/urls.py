"""
    URL configuration for mini project.
    
    The `urlpatterns` list routes URLs to views. For more information please see:
        https://docs.djangoproject.com/en/4.2/topics/http/urls/
    Examples:
    Function views
        1. Add an import:  from my_app import views
        2. Add a URL to urlpatterns:  path('', views.home, name='home')
    Class-based views
        1. Add an import:  from other_app.views import Home
        2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
    Including another URLconf
        1. Import the include() function: from django.urls import include, path
        2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
    
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import admin

urlpatterns = [
    # Default Django admin (not used in your app, but still good to keep)
    path('admin/', admin.site.urls),

    path('', lambda request: redirect('login', permanent=False)),
    # ─────────── ACCOUNTS ───────────

    # USER login, register, profile, password reset
    path('accounts/', include('accounts.urls.user_urls')),

    # ADMIN (Superadmin) login, logout, dashboard
    path('adminpanel/', include('accounts.urls.admin_urls')),  # <-- This is now clean and separate

    # ADDRESS MANAGEMENT (used by both user and during checkout)
    path('accounts/addresses/', include('accounts.urls.address_urls')),

    # ─────────── CORE APPS ───────────

    path('products/', include('products.urls')),
    
    path('cart/', include('cart.urls')),

    
    path('orders/', include('orders.urls')),
    path('orders/', include('orders.urls.checkout_urls')),
    path('orders/', include('orders.urls.order_user_urls')),
    path('orders/', include('orders.urls.order_admin_urls')),
    # ─────────── WISHLIST ───────────
    path('wishlist/', include('wishlist.urls')),
]

# ─────────── MEDIA FILES ───────────
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

