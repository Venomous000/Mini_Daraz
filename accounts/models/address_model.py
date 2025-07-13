from django.db import models
from django.conf import settings
from accounts.models.base import TimeStampedModel, PhoneNumberModel

# 🚀 This model will be added soon, just referenced here
# from accounts.models import GuestUser

class Address(TimeStampedModel, PhoneNumberModel):
    """
    Address model for both authenticated users and guest users.
    Only one default address is allowed per user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses',
        null=True, blank=True
    )
    guest = models.ForeignKey(
        'accounts.GuestUser',  # You’ll create this model next
        on_delete=models.CASCADE,
        related_name='guest_addresses',
        null=True, blank=True
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
        if self.user and self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def belongs_to(self, user_or_guest):
        return self.user == user_or_guest or self.guest == user_or_guest

    @classmethod
    def get_user_address(cls, user, address_id):
        return cls.objects.filter(user=user, pk=address_id).first()

    @classmethod
    def create_for_user(cls, user, address_data, is_default=False):
        address = cls(
            user=user,
            full_name=address_data.get("full_name", user.name),
            phone=address_data.get("phone", user.phone),
            street_address=address_data.get("street_address"),
            zip_code=address_data.get("zip_code"),
            city=address_data.get("city"),
            province=address_data.get("province"),
            country=address_data.get("country"),
            is_default=is_default,
        )
        address.save()
        return address

    @classmethod
    def create_for_guest(cls, guest, address_data):
        address = cls(
            guest=guest,
            full_name=address_data.get("full_name"),
            phone=address_data.get("phone"),
            street_address=address_data.get("street_address"),
            zip_code=address_data.get("zip_code"),
            city=address_data.get("city"),
            province=address_data.get("province"),
            country=address_data.get("country"),
        )
        address.save()
        return address
