from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.models.address_model import Address
from accounts.forms import AddressForm

@login_required
def manage_addresses(request):
    addresses = request.user.addresses.all()
    return render(request, 'accounts/manage_addresses.html', {'addresses': addresses})


@login_required
def add_address(request):
    form = AddressForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.save()
        messages.success(request, 'Address added successfully.')
        return redirect('manage_addresses')
    return render(request, 'accounts/add_address.html', {'form': form})


@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, pk=address_id, user=request.user)
    form = AddressForm(request.POST or None, instance=address)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Address updated successfully.')
        return redirect('manage_addresses')
    return render(request, 'accounts/edit_address.html', {'form': form, 'address': address})


@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, pk=address_id, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully.')
        return redirect('manage_addresses')
    return render(request, 'accounts/confirm_delete_address.html', {'address': address})
