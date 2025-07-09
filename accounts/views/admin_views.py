from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.models.admin_model import Admin
from accounts.decorators.superadmin_required import superadmin_required


def superadmin_login_view(request):
    """
    Handles manual superadmin login.
    Only one Admin instance is allowed.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"DEBUG: Attempt login with {username=} {password=}")
        admin = Admin.authenticate(username=username, password=password)
        if admin:
            request.session['superadmin_id'] = admin.id
            return redirect('admin_dashboard')
        messages.error(request, 'Invalid superadmin credentials.')
    return render(request, 'accounts/superadmin_login.html')


def superadmin_logout_view(request):
    """
    Clears superadmin session and logs out.
    """
    request.session.flush()
    return redirect('superadmin_login')


@superadmin_required
def admin_dashboard(request):
    """
    Basic dashboard after superadmin logs in.
    """
    return render(request, 'accounts/admin_dashboard.html')
