from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from decimal import Decimal
from products.models import Product
from orders.models import Order


def guest_cart_checkout(request):
    session_cart = request.session.get('cart', {})
    if not session_cart:
        messages.error(request, "Your cart is empty.")
        return redirect('home')

    cart_items = []
    total_price = Decimal('0.00')

    for pid, qty in session_cart.items():
        try:
            product = Product.objects.get(pk=pid)
            subtotal = qty * product.price_per_piece
            cart_items.append({
                'product': product,
                'quantity': qty,
                'subtotal': subtotal,
            })
            total_price += subtotal
        except Product.DoesNotExist:
            continue

    if request.method == 'POST':
        guest_info = {
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
        }
        address_data = {
            'street_address': request.POST.get('street_address'),
            'city': request.POST.get('city'),
            'province': request.POST.get('province'),
            'country': request.POST.get('country'),
            'zip_code': request.POST.get('zip_code'),
        }
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
            try:
                items = []
                for pid, qty in session_cart.items():
                    product = Product.objects.get(pk=pid)
                    items.append({
                        'product': product,
                        'quantity': qty,
                        'unit_price': product.price_per_piece
                    })

                order = Order.create_guest_order(
                    guest_data={**guest_info, **address_data},
                    cart_items=items,
                    skip_clear=True
                )

                session = order.create_stripe_session(
                    success_url=request.build_absolute_uri(reverse("guest_order_success")),
                    cancel_url=request.build_absolute_uri(reverse("guest_cart_checkout"))
                )
                return redirect(session.url)

            except Exception as e:
                messages.error(request, str(e))
                return redirect('guest_cart_checkout')

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

    if not guest_cart or not guest_info or not address_data:
        messages.error(request, "Incomplete guest checkout data.")
        return redirect("guest_cart_checkout")

    try:
        cart_items = []
        for pid, qty in guest_cart.items():
            product = Product.objects.get(pk=pid)
            cart_items.append({
                'product': product,
                'quantity': qty,
                'unit_price': product.price_per_piece,
            })

        Order.create_guest_order(
            guest_data={**guest_info, **address_data},
            cart_items=cart_items
        )

        request.session.pop("guest_checkout", None)
        request.session.pop("cart", None)
        messages.success(request, "Order placed successfully as guest.")
        return redirect("guest_order_success")

    except Exception as e:
        messages.error(request, str(e))
        return redirect("guest_cart_checkout")


def guest_buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    request.session['guest_cart'] = [{
        'product_id': product.id,
        'quantity': 1,
    }]
    request.session.modified = True
    return redirect("guest_checkout")


def guest_checkout_view(request):
    cart_items = request.session.get("guest_cart", [])

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect("guest_cart_checkout")

    if request.method == "POST":
        guest_info = {
            "name": request.POST.get("name"),
            "email": request.POST.get("email"),
            "phone": request.POST.get("phone"),
        }
        address_info = {
            "street_address": request.POST.get("street_address"),
            "city": request.POST.get("city"),
            "province": request.POST.get("province"),
            "country": request.POST.get("country"),
            "zip_code": request.POST.get("zip_code"),
        }
        payment_method = request.POST.get("payment_method")

        parsed_items = []
        for item in cart_items:
            try:
                product = Product.objects.get(id=item["product_id"])
                quantity = int(item["quantity"])
                if quantity > product.stock_quantity:
                    messages.error(request, f"Not enough stock for {product.product_name}")
                    return redirect("guest_cart_checkout")
                parsed_items.append({
                    "product": product,
                    "quantity": quantity,
                    "unit_price": product.price_per_piece,
                })
            except Product.DoesNotExist:
                messages.error(request, "One of the products no longer exists.")
                return redirect("guest_cart_checkout")

        try:
            order = Order.create_guest_order(
                guest_data={**guest_info, **address_info},
                cart_items=parsed_items
            )

            if payment_method == "cod":
                return redirect("guest_order_success")

            elif payment_method == "online":
                success_url = request.build_absolute_uri(reverse("guest_order_success"))
                cancel_url = request.build_absolute_uri(reverse("guest_cart_checkout"))
                session = order.create_stripe_session(success_url, cancel_url)
                return redirect(session.url)

            else:
                messages.error(request, "Invalid payment method selected.")
                return redirect("guest_cart_checkout")

        except Exception as e:
            messages.error(request, f"Error processing your order: {e}")
            return redirect("guest_cart_checkout")

    context_items = []
    total_price = 0
    for item in cart_items:
        product = Product.objects.get(id=item["product_id"])
        quantity = item["quantity"]
        subtotal = product.price_per_piece * quantity
        context_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })
        total_price += subtotal

    return render(request, 'orders/checkout_buy_now.html', {
        'product': product,
        'quantity': 1,
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
