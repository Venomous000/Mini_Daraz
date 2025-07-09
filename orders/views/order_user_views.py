from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order

@login_required
def order_history(request):
    orders = request.user.orders.select_related('user').prefetch_related('items__product')
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Order deleted successfully.')
        return redirect('order_history')

    return render(request, 'orders/confirm_delete_order.html', {'order': order})

