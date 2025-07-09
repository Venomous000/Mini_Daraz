from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from wishlist.models import Wishlist


@login_required
def view_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist/view_wishlist.html', {
        'wishlist_items': wishlist_items
    })


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        Wishlist.add(request.user, product)
        messages.success(request, "Product added to your wishlist.")
    except ValueError as e:
        messages.info(request, str(e))

    return redirect(request.GET.get('next', 'home'))


@login_required
def remove_from_wishlist(request, product_id):
    try:
        Wishlist.remove(request.user, product_id)
        messages.success(request, "Removed from wishlist.")
    except ValueError as e:
        messages.warning(request, str(e))

    return redirect(request.GET.get('next', 'view_wishlist'))


@login_required
def move_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        Wishlist.move_to_cart(request.user, product)
        messages.success(request, "Moved to cart.")
    except ValueError as e:
        messages.error(request, str(e))

    return redirect(request.GET.get('next', 'view_wishlist'))
