import stripe
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from orders.models import Order
from accounts.models import Address
from products.models import Product
from cart.models import Cart

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def start_stripe_checkout_cart(request):
    address_id = request.session.get("selected_address_id")
    cart = Cart.objects.filter(user=request.user).first()

    if not cart or not address_id:
        messages.error(request, "Missing cart or address.")
        return redirect("cart_checkout")

    address = get_object_or_404(Address, id=address_id, user=request.user)

    try:
        order = Order.create_from_cart(request.user, cart, address)
        session = order.create_stripe_session(
            success_url=request.build_absolute_uri("/orders/payment-success/user/"),
            cancel_url=request.build_absolute_uri("/orders/cart/checkout/")
        )
        return redirect(session.url, code=303)
    except Exception as e:
        messages.error(request, str(e))
        return redirect("cart_checkout")


@login_required
def start_stripe_checkout_buy_now(request):
    product_id = request.session.get("buy_now_product_id")
    address_id = request.session.get("selected_address_id")

    if not product_id or not address_id:
        messages.error(request, "Missing product or address.")
        return redirect("checkout_buy_now")

    product = get_object_or_404(Product, id=product_id)
    address = get_object_or_404(Address, id=address_id, user=request.user)

    try:
        order = Order.create_buy_now(request.user, product, address)
        session = order.create_stripe_session(
            success_url=request.build_absolute_uri("/orders/payment-success/user/"),
            cancel_url=request.build_absolute_uri("/orders/checkout/buy-now/")
        )
        return redirect(session.url, code=303)
    except Exception as e:
        messages.error(request, str(e))
        return redirect("checkout_buy_now")


@login_required
def payment_success_user(request):
    try:
        order = Order.objects.filter(user=request.user, paid=False, payment_method="stripe").latest("order_date")
        order.mark_paid()
        messages.success(request, "Payment successful and order placed!")
        return redirect("order_history")
    except Order.DoesNotExist:
        messages.error(request, "Order not found or already paid.")
        return redirect("home")
