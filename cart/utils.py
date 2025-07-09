# cart/utils.py

def get_session_cart(request):
    return request.session.get('cart', {})


def save_session_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def add_to_session_cart(request, product_id, quantity=1):
    cart = get_session_cart(request)
    product_id = str(product_id)
    if product_id in cart:
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity
    save_session_cart(request, cart)


def remove_from_session_cart(request, product_id):
    cart = get_session_cart(request)
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
        save_session_cart(request, cart)


def clear_session_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
        request.session.modified = True
