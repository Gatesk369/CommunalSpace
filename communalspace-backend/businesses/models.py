from django.db import models
from accounts.models import User


# Create your models here.
class Business(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": User.BUSINESS_OWNER},
        related_name="businesses",
    )
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class BusinessOwnerHistory(models.Model):
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="owner_history"
    )
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="owner_history"
    )
    transferred_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business.name} - {self.transferred_at}"
