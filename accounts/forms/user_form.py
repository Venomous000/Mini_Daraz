from django import forms
from accounts.models import User
import random
import string


class UserRegistrationForm(forms.ModelForm):
    """
    Registration form with built-in username suggestion and validation.
    """
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'name', 'phone', 'password', 'confirm_password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Suggest a username based on name, only if not already entered
        if not self.data.get("username"):  # During POST
            name_value = self.data.get("name") or self.initial.get("name")
            if name_value:
                self.fields["username"].initial = self.generate_username(name_value)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("Username is required.")
        if not User.objects.is_username_available(username):
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def generate_username(self, base):
        """
        Suggest a random username from a base string.
        """
        base = ''.join(e for e in base.lower() if e.isalnum())
        suggestions = [
            f"{base}{random.randint(10, 99)}",
            f"{base}_{random.choice(string.ascii_lowercase)}{random.randint(100, 999)}",
            f"{base}{random.randint(1000, 9999)}",
        ]
        for uname in suggestions:
            if User.objects.is_username_available(uname):
                return uname
        return f"{base}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}"

    def save(self, commit=True):
        data = self.cleaned_data
        return User.objects.create_user(
            email=data['email'],
            username=data['username'],
            name=data['name'],
            password=data['password'],
            phone=data.get('phone')
        )


class UserLoginForm(forms.Form):
    """
    Username-based login form.
    """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
