from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect
from accounts.models.user_model import User


class CustomPasswordResetView(PasswordResetView):
    """
    Custom password reset view that sends password reset link via email.
    """
    template_name = 'accounts/password_reset_form.html'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        users = User.objects.filter(email=email)
        if users.exists():
            for user in users:
                context = {
                    'email': user.email,
                    'domain': self.request.get_host(),
                    'site_name': 'MiniDaraz',
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'user': user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'https' if self.request.is_secure() else 'http',
                }
                subject = 'Reset Your Password'
                email_message = render_to_string('accounts/reset_password_email.html', context)
                send_mail(subject, email_message, settings.DEFAULT_FROM_EMAIL, [user.email])

            # 👇 Don't call super().form_valid(form) which would resend email
            messages.success(self.request, "We've sent you a password reset link.")
            return redirect(self.success_url)
        else:
            messages.error(self.request, 'No user found with this email.')
            return self.form_invalid(form)
