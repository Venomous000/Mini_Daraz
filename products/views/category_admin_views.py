from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import superadmin_required
from products.models import Category
from products.forms import CategoryForm


@superadmin_required
def add_category(request):
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category added successfully.')
        return redirect('add_category')

    categories = Category.objects.all()
    return render(request, 'products/admin_add_category.html', {
        'form': form,
        'categories': categories
    })


@superadmin_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    form = CategoryForm(request.POST or None, instance=category)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category updated successfully.')
        return redirect('add_category')

    categories = Category.objects.all()
    return render(request, 'products/admin_add_category.html', {
        'form': form,
        'categories': categories
    })


@superadmin_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, "Category deleted successfully.")
    return redirect('add_category')
