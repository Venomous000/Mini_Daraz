from celery import shared_task
from django.core.mail import send_mail
from wishlist.models import Wishlist
from products.models import Product
from django.conf import settings


@shared_task
def notify_users_of_product_update(product_id, changes):
    product = Product.objects.filter(pk=product_id).first()
    if not product:
        return

    wishlisted_users = Wishlist.objects.filter(product=product).select_related("user")

    for item in wishlisted_users:
        user = item.user
        if not user.email:
            continue

        subject = f"Update on {product.product_name}"

        message = f"Dear {user.name},\n\n"
        message += f"The product **{product.product_name}** on your wishlist has changed:\n\n"

        if "price_changed" in changes:
            old = changes["price_changed"]["old"]
            new = changes["price_changed"]["new"]
            if new < old:
                message += f"• Price dropped from ${old} to ${new}"
            else:
                message += f"• Price increased from ${old} to ${new}"

        if "stock_changed" in changes:
            old = changes["stock_changed"]["old"]
            new = changes["stock_changed"]["new"]
            if new < old:
                message += f"• Stock decreased from {old} to {new}"
            else:
                message += f"• Stock increased from {old} to {new}"

        message += f"\nCheck it out here: http://127.0.0.1:8000/products/product/{product.id}/"

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
