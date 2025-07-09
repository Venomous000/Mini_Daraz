from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from cart.models import Cart

#  Add to Cart 
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        try:
            cart.add_product(product, quantity)
            messages.success(request, "Product added to cart.")
        except ValueError as e:
            messages.warning(request, str(e))
        return redirect(request.POST.get('next', 'home'))

    # Guest user — store in session
    session_cart = request.session.get('cart', {})
    pid_str = str(product.id)
    session_cart[pid_str] = session_cart.get(pid_str, 0) + quantity
    request.session['cart'] = session_cart
    messages.success(request, "Product added to cart. Please login to complete your order.")
    return redirect(request.POST.get('next', 'home'))

#  View Cart 
@login_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart.update_total_price()
    return render(request, 'cart/view_cart.html', {
        'cart_items': cart.items.select_related('product').all(),
        'total_price': cart.total_price,
    })

#  Guest-to-Login Cart Redirect 
def view_cart_redirect(request):
    if request.user.is_authenticated:
        return redirect('view_cart')
    messages.warning(request, "Please login to view your cart.")
    request.session["next"] = "view_cart"
    return redirect("login")

#  Remove Item 
@login_required
def remove_from_cart(request, cart_item_id):
    cart = get_object_or_404(Cart, user=request.user)
    if request.method == 'POST':
        try:
            cart.remove_item(cart_item_id)
            messages.success(request, "Item removed from cart.")
        except Exception:
            messages.error(request, "Unable to remove item.")
    return redirect('view_cart')

#  Update Item
@login_required
def update_cart_item(request, cart_item_id):
    cart = get_object_or_404(Cart, user=request.user)
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            cart.update_item_quantity(cart_item_id, quantity)
            messages.success(request, "Cart updated successfully.")
        except ValueError as e:
            messages.error(request, str(e))
        except Exception:
            messages.error(request, "Unable to update cart item.")
    return redirect('view_cart')
