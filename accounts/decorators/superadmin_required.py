from django.shortcuts import redirect
from django.contrib import messages

def superadmin_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.session.get('superadmin_id'):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Superadmin access required.")
            return redirect('superadmin_login')  # Change to your correct login view name
    return wrapper_func