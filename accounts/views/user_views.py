
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash, authenticate
from django.contrib.auth.decorators import login_required
from accounts.forms import UserRegistrationForm, UserLoginForm
from accounts.models.user_model import User


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


from cart.models import Cart  # ← import Cart for merge

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)

                session_cart = request.session.get("cart")
                if session_cart:
                    Cart.objects.merge_session_cart(user, session_cart)
                    del request.session["cart"]

                next_url = request.session.pop("next", None)
                return redirect(next_url or 'home')

            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def view_profile(request):
    return render(request, 'accounts/view_profile.html', {'user': request.user})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        request.user.update_profile(name=name, phone=phone)
        messages.success(request, "Profile updated successfully.")
        return redirect('view_profile')
    return render(request, 'accounts/edit_profile.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        current = request.POST.get('current_password')
        new = request.POST.get('new_password')
        success, error = request.user.change_password(current, new)
        if success:
            update_session_auth_hash(request, request.user)
            messages.success(request, "Password updated successfully.")
            return redirect('view_profile')
        else:
            messages.error(request, error)
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')
