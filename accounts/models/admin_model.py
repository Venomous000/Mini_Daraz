from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Admin(models.Model):
    """Manual superadmin model with enforced singleton behavior."""
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.pk and Admin.objects.exists():
            raise Exception("Only ne superadmin can exist.")
    
    # Only hash if not already hashed
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    def verify_password(self, raw_password):
        return check_password(raw_password, self.password)

    @classmethod
    def authenticate(cls, username, password):
        try:
            admin = cls.objects.get(username=username)
            if admin.verify_password(password):
                return admin
        except cls.DoesNotExist:
            return None
