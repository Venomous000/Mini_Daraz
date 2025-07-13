from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from products.models import Product
from orders.models import Order
from accounts.models import GuestUser, Address

# ===== Helpers =====

def extract_guest_data(request):
    return {
        'name': request.POST.get('name'),
        'email': request.POST.get('email'),
        'phone': request.POST.get('phone'),
    }

def extract_address_data(request):
    return {
        'street_address': request.POST.get('street_address'),
        'city': request.POST.get('city'),
        'province': request.POST.get('province'),
        'country': request.POST.get('country'),
        'zip_code': request.POST.get('zip_code'),
    }

def process_guest_order(request, guest_info, address_data, cart_items, payment_method):
    try:
        order = Order.create_guest_order(
            guest_data={**guest_info, **address_data, "payment_method": payment_method},
            cart_items=cart_items
        )

        if payment_method == "cod":
            return redirect("guest_order_success")

        elif payment_method in ["stripe", "online"]:
            success_url = request.build_absolute_uri(reverse("guest_order_success"))
            cancel_url = request.build_absolute_uri(reverse("guest_cart_checkout"))
            session = order.create_stripe_session(success_url, cancel_url)
            return redirect(session.url)

        messages.error(request, "Invalid payment method selected.")
        return redirect("guest_cart_checkout")

    except Exception as e:
        messages.error(request, f"Error processing your order: {e}")
        return redirect("guest_cart_checkout")


# ===== Views =====

def guest_cart_checkout(request):
    session_cart = request.session.get('cart', {})
    if not session_cart:
        messages.error(request, "Your cart is empty.")
        return redirect('home')

    cart_items, total_price = Order.parse_guest_cart_items(session_cart)

    if request.method == 'POST':
        guest_info = extract_guest_data(request)
        address_data = extract_address_data(request)
        payment_method = request.POST.get('payment_method')

        if not all(guest_info.values()) or not all(address_data.values()):
            messages.error(request, "Please fill in all required fields.")
            return redirect('guest_cart_checkout')

        request.session["guest_checkout"] = {
            "cart": session_cart,
            "guest_info": guest_info,
            "address": address_data,
            "payment_method": payment_method,
        }

        if payment_method == "online":
            return process_guest_order(request, guest_info, address_data, cart_items, payment_method)

        return redirect("place_cart_order_guest")

    return render(request, 'orders/cart_checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'user_type': 'guest',
        'session_cart_items': cart_items,
    })


def place_cart_order_guest(request):
    session_data = request.session.get("guest_checkout", {})
    guest_cart = session_data.get("cart", {})
    guest_info = session_data.get("guest_info", {})
    address_data = session_data.get("address", {})
    payment_method = session_data.get("payment_method", "cod")

    if not guest_cart or not guest_info or not address_data:
        messages.error(request, "Incomplete guest checkout data.")
        return redirect("guest_cart_checkout")

    cart_items, _ = Order.parse_guest_cart_items(guest_cart)
    result = process_guest_order(request, guest_info, address_data, cart_items, payment_method)
    request.session.pop("guest_checkout", None)
    request.session.pop("cart", None)
    return result


def guest_buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    request.session['guest_cart'] = [{
        'product_id': product.id,
        'quantity': 1,
    }]
    request.session.modified = True
    return redirect("guest_checkout")


def guest_checkout_view(request):
    cart_items_data = request.session.get("guest_cart", [])

    if not cart_items_data:
        messages.error(request, "Your cart is empty.")
        return redirect("guest_cart_checkout")

    cart_items, total_price = Order.parse_guest_cart_items(cart_items_data)

    if request.method == "POST":
        guest_info = extract_guest_data(request)
        address_data = extract_address_data(request)
        payment_method = request.POST.get("payment_method")
        return process_guest_order(request, guest_info, address_data, cart_items, payment_method)

    return render(request, 'orders/checkout_buy_now.html', {
        'product': cart_items[0]['product'],
        'quantity': cart_items[0]['quantity'],
        'total_price': total_price,
        'addresses': [],
        'user_type': 'guest',
    })


def place_guest_buy_now_order(request):
    session_data = request.session.get("guest_buy_now_data")
    if not session_data:
        messages.error(request, "Missing guest data.")
        return redirect("guest_checkout")

    try:
        product = get_object_or_404(Product, id=session_data["product_id"])
        if product.stock_quantity < 1:
            raise ValueError("Product is out of stock.")

        Order.create_guest_order(
            guest_data={**session_data["guest_info"], **session_data["address"]},
            cart_items=[{
                'product': product,
                'quantity': 1,
                'unit_price': product.price_per_piece
            }]
        )

        request.session.pop("guest_buy_now_data", None)
        request.session.pop("guest_cart", None)
        messages.success(request, "Order placed successfully as guest.")
        return redirect("guest_order_success")

    except Exception as e:
        messages.error(request, str(e))
        return redirect("guest_checkout")


def guest_order_success(request):
    return render(request, 'orders/guest_order_success.html')


def buy_now_entry_point(request, product_id):
    if request.user.is_authenticated:
        return redirect('buy_now', product_id=product_id)

    request.session['pending_buy_now_product_id'] = product_id
    return render(request, 'orders/guest_or_login_choice.html', {
        'product_id': product_id
    })
