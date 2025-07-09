from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import superadmin_required
from products.models import Product, ProductImage
from products.forms import ProductImageForm


@superadmin_required
def upload_product_image(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = ProductImageForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        product_image = form.save(commit=False)
        product_image.product = product
        product_image.save()
        messages.success(request, 'Image uploaded and resized successfully.')
        return redirect('admin_product_list')

    return render(request, 'products/admin_upload_product_image.html', {'form': form, 'product': product})


@superadmin_required
def delete_product_image(request, image_id):
    image = get_object_or_404(ProductImage, id=image_id)
    product_id = image.product.id
    image.delete()
    messages.success(request, "Image deleted successfully.")
    return redirect('edit_product', product_id=product_id)
