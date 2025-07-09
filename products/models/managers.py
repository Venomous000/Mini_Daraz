from django.db import models


class ProductManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)

    def search(self, query=None, category_id=None):
        products = self.active()
        if query:
            products = products.filter(product_name__icontains=query)
        if category_id:
            products = products.filter(category_id=category_id)
        return products
