import os
from django.db import models
from PIL import Image
from .product_model import Product


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.product_name}"

    def delete_image_file(self):
        """Physically delete image file from disk."""
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)

    def delete(self, *args, **kwargs):
        self.delete_image_file()
        super().delete(*args, **kwargs)

    def resize_image(self, size=(500, 500)):
        """Resize uploaded image while maintaining aspect ratio."""
        if self.image:
            with Image.open(self.image.path) as img:
                img.thumbnail(size)
                img.save(self.image.path)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.resize_image()
