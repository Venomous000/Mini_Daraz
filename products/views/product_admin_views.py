from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import superadmin_required
from products.models import Product
from products.forms import ProductForm


@superadmin_required
def admin_product_list(request):
    products = Product.objects.all()
    return render(request, 'products/admin_product_list.html', {'products': products})


@superadmin_required
def add_product(request):
    form = ProductForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product added successfully.')
        return redirect('admin_product_list')
    return render(request, 'products/admin_add_product.html', {'form': form})


@superadmin_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product updated successfully.')
        return redirect('admin_product_list')
    return render(request, 'products/admin_edit_product.html', {'form': form, 'product': product})


@superadmin_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Product deleted successfully.')
    return redirect('admin_product_list')
