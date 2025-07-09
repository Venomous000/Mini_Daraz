from django.db import models
from django.conf import settings
from accounts.models.base import TimeStampedModel, PhoneNumberModel


class Address(TimeStampedModel, PhoneNumberModel):
    """
    Address model for user delivery addresses.
    Only one default address is allowed per user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    full_name = models.CharField(max_length=100)
    street_address = models.TextField()
    zip_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name}, {self.city}, {self.province}"

    def save(self, *args, **kwargs):
        # Ensure only one default address per user
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def belongs_to(self, user):
        return self.user == user

    @classmethod
    def get_user_address(cls, user, address_id):
        return cls.objects.filter(user=user, pk=address_id).first()
