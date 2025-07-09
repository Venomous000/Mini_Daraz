from django.db import models

class TimeStampedModel(models.Model):
    """Reusable abstract base model for timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PhoneNumberModel(models.Model):
    """Reusable abstract base model for phone numbers."""
    phone = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        abstract = True
