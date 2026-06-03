from django.db import models


# Create your models here.
class Business(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "business owner"},
        related_name="businesses",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class BusinessBranch(models.Model):
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="branches"
    )
    community = models.ForeignKey(
        "communities.Community",
        on_delete=models.SET_NULL,
        null=True,
        related_name="businesses",
    )
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=25)
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)


class BusinessOwnerHistory(models.Model):
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="owner_history"
    )
    owner = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="owner_history",
    )
    transferred_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business.name} - {self.transferred_at}"
