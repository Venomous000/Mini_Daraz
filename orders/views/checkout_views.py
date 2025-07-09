from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from accounts.models import Address
from products.models import Product
from cart.models import Cart
from orders.models import Order


@login_required
def cart_checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("view_cart")

    addresses = request.user.addresses.all()

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        selected_id = request.POST.get("selected_address")
        address_data = {
            'street_address': request.POST.get('street_address'),
            'city': request.POST.get('city'),
            'province': request.POST.get('province'),
            'country': request.POST.get('country'),
            'zip_code': request.POST.get('zip_code'),
        }

        if selected_id:
            request.session["selected_address_id"] = selected_id
        elif all(address_data.values()):
            new_address = Address.create_for_user(request.user, address_data)
            request.session["selected_address_id"] = new_address.id
        else:
            messages.error(request, 'Please select or provide a valid address.')
            return redirect("cart_checkout")

        if payment_method == 'stripe':
            try:
                address = get_object_or_404(Address, id=request.session["selected_address_id"])
                order = Order.create_from_cart(user=request.user, cart=cart, address=address)
                request.session.pop("selected_address_id", None)

                session = order.create_stripe_session(
                    success_url=request.build_absolute_uri(reverse("order_success")),
                    cancel_url=request.build_absolute_uri(reverse("view_cart"))
                )
                return redirect(session.url)

            except Exception as e:
                messages.error(request, str(e))
                return redirect("cart_checkout")

        return redirect("place_cart_order")

    return render(request, "orders/cart_checkout.html", {
        "cart_items": cart.items.all(),
        "total_price": cart.total_price,
        "addresses": addresses,
        "user_type": "logged_in",
    })


@login_required
def place_cart_order(request):
    cart = Cart.objects.filter(user=request.user).first()
    address_id = request.session.get("selected_address_id")

    if not cart or not address_id:
        messages.error(request, "Missing cart or address.")
        return redirect("cart_checkout")

    address = get_object_or_404(Address, id=address_id, user=request.user)

    try:
        Order.create_from_cart(user=request.user, cart=cart, address=address)
        request.session.pop("selected_address_id", None)
        messages.success(request, "Order placed successfully!")
        return redirect("order_history")

    except ValueError as e:
        messages.error(request, str(e))
        return redirect("cart_checkout")


@login_required
def buy_now(request, product_id):
    request.session['buy_now_product_id'] = product_id
    return redirect('checkout_buy_now')


@login_required
def checkout_buy_now(request):
    product_id = request.session.get('buy_now_product_id')
    if not product_id:
        messages.error(request, "No product selected.")
        return redirect("user_home")

    product = get_object_or_404(Product, id=product_id)
    addresses = request.user.addresses.all()

    if request.method == 'POST':
        payment_method = request.POST.get("payment_method")
        selected_id = request.POST.get("selected_address")
        address_data = {
            'street_address': request.POST.get('street_address'),
            'city': request.POST.get('city'),
            'province': request.POST.get('province'),
            'country': request.POST.get('country'),
            'zip_code': request.POST.get('zip_code'),
        }

        if selected_id:
            request.session["selected_address_id"] = selected_id
        elif all(address_data.values()):
            new_address = Address.create_for_user(request.user, address_data)
            request.session["selected_address_id"] = new_address.id
        else:
            messages.error(request, 'Please select or provide a valid address.')
            return redirect("checkout_buy_now")

        if payment_method == 'stripe':
            try:
                address = get_object_or_404(Address, id=request.session["selected_address_id"])
                order = Order.create_buy_now(user=request.user, product=product, address=address)
                request.session.pop("selected_address_id", None)
                request.session.pop("buy_now_product_id", None)

                session = order.create_stripe_session(
                    success_url=request.build_absolute_uri(reverse("order_success")),
                    cancel_url=request.build_absolute_uri(reverse("user_home"))
                )
                return redirect(session.url)

            except Exception as e:
                messages.error(request, str(e))
                return redirect("checkout_buy_now")

        return redirect("place_buy_now_order")

    return render(request, "orders/checkout_buy_now.html", {
        "product": product,
        "addresses": addresses,
    })


@login_required
def place_buy_now_order(request):
    product_id = request.session.get('buy_now_product_id')
    address_id = request.session.get('selected_address_id')

    if not product_id or not address_id:
        messages.error(request, "Missing product or address.")
        return redirect("checkout_buy_now")

    product = get_object_or_404(Product, id=product_id)
    address = get_object_or_404(Address, id=address_id, user=request.user)

    try:
        Order.create_buy_now(user=request.user, product=product, address=address)
        messages.success(request, "Buy Now order placed successfully!")

    except ValueError as e:
        messages.error(request, str(e))

    request.session.pop("buy_now_product_id", None)
    request.session.pop("selected_address_id", None)

    return redirect("order_history")
