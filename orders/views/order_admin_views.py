from django.shortcuts import render, get_object_or_404
from accounts.decorators import superadmin_required
from orders.models import Order

@superadmin_required
def admin_order_list(request):
    filters = {
        'user_email': request.GET.get('q'),
        'city': request.GET.get('city'),
        'province': request.GET.get('province'),
        'country': request.GET.get('country'),
        'zip_code': request.GET.get('zip_code'),
    }

    orders = Order.filter_by_criteria(**filters)

    return render(request, 'orders/admin_order_list.html', {
        'orders': orders,
        **filters
    })


@superadmin_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/admin_order_detail.html', {
        'order': order,
        'order_items': order.items.select_related('product'),
    })
