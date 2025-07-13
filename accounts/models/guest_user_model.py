from django.db import models
from accounts.models.base import TimeStampedModel, PhoneNumberModel


class GuestUser(TimeStampedModel, PhoneNumberModel):
    """
    A model to store guest user identities for order tracking.
    Each guest user record is unique and independent per order/session.
    """
    guest_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    session_key = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Guest {self.guest_id} - {self.email}"

    @classmethod
    def create_guest(cls, name, email, phone, session_key=None):
        last_guest = cls.objects.order_by('-id').first()
        new_number = 1 if not last_guest else last_guest.id + 1
        guest_id = f"guest_{new_number:06d}"

        guest = cls.objects.create(
            guest_id=guest_id,
            name=name,
            email=email,
            phone=phone,
            session_key=session_key or ''
        )
        return guest
