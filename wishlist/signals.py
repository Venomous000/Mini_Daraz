from django.db.models.signals import pre_save
from django.dispatch import receiver
from wishlist.models import Wishlist
from products.models import Product
from wishlist.tasks import notify_users_of_product_update


@receiver(pre_save, sender=Product)
def product_update_notifier(sender, instance, **kwargs):
    try:
        original = Product.objects.get(pk=instance.pk)
    except Product.DoesNotExist:
        return  # New product, no need to notify

    changes = {}

    # Price comparison
    if original.price != instance.price:
        percent_change = ((original.price - instance.price) / original.price) * 100
        if abs(percent_change) >= 10:
            changes["price_changed"] = {
                "old": float(original.price),
                "new": float(instance.price)
            }

    # Stock comparison
    if original.quantity != instance.quantity:
        percent_change = ((original.quantity - instance.quantity) / original.quantity) * 100 if original.quantity else 100
        if abs(percent_change) >= 25:
            changes["stock_changed"] = {
                "old": original.quantity,
                "new": instance.quantity
            }

    if changes:
        notify_users_of_product_update.delay(instance.pk, changes)
