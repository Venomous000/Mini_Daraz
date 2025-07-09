from django.shortcuts import render, get_object_or_404
from products.models import Product, Category


def user_home(request):
    search_query = request.GET.get('search')
    category_filter = request.GET.get('category')

    products = Product.objects.search(query=search_query, category_id=category_filter)
    categories = Category.objects.all()

    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist_product_ids = request.user.wishlist_items.values_list('product_id', flat=True)

    return render(request, 'products/user_home.html', {
        'products': products,
        'categories': categories,
        'wishlist_product_ids': wishlist_product_ids
    })



def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist_product_ids = request.user.wishlist_items.values_list('product_id', flat=True)

    return render(request, 'products/product_detail.html', {
        'product': product,
        'wishlist_product_ids': wishlist_product_ids
    })
