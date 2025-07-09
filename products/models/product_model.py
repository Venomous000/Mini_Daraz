from django.db import models
from .category_model import Category
from .managers import ProductManager

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    stock_quantity = models.PositiveIntegerField(default=0)
    price_per_piece = models.DecimalField(max_digits=10, decimal_places=2)
    product_description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductManager()

    def __str__(self):
        return self.product_name

    def deactivate(self):
        """Soft-delete product."""
        self.is_active = False
        self.save()

    def primary_image(self):
        """Return first image or None (fallback handled in template)."""
        return self.images.first()
        
    def save(self, *args, **kwargs):
        from wishlist.tasks import notify_users_of_product_update

        # Check if updating existing product
        if self.pk:
            old = Product.objects.get(pk=self.pk)

            changes = {}
            if self.price_per_piece != old.price_per_piece:
                changes["price_changed"] = {
                    "old": old.price_per_piece,
                    "new": self.price_per_piece,
                }

            if self.stock_quantity != old.stock_quantity:
                changes["stock_changed"] = {
                    "old": old.stock_quantity,
                    "new": self.stock_quantity,
                }

            # Save before calling async task
            super().save(*args, **kwargs)

            # Only call Celery task if there are changes
            if changes:
                notify_users_of_product_update.delay(self.pk, changes)

        else:
            # New product — normal save
            super().save(*args, **kwargs)