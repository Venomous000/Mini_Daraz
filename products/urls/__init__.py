from .product_user_urls import urlpatterns as product_user_urls
from .admin_product_urls import urlpatterns as admin_product_urls
from .admin_category_urls import urlpatterns as admin_category_urls

urlpatterns = product_user_urls + admin_product_urls + admin_category_urls