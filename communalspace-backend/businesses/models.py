from accounts.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# Create your models here.
class Business(models.Model):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
    )

    FOOD_AND_DINING = "food_and_dining"
    RETAIL_AND_SHOPPING = "retail_and_shopping"
    HEALTH_AND_WELLNESS = "health_and_wellness"
    HOME_AND_REPAIR_SERVICES = "home_and_repair_services"
    PROFESSIONAL_SERVICES = "professional_services"
    EDUCATION = "education"
    OTHER = "other"

    CATEGORY_CHOICES = (
        (FOOD_AND_DINING, "Food & Dining"),
        (RETAIL_AND_SHOPPING, "Retail & Shopping"),
        (HEALTH_AND_WELLNESS, "Health & Wellness"),
        (HOME_AND_REPAIR_SERVICES, "Home & Repair Services"),
        (PROFESSIONAL_SERVICES, "Professional Services"),
        (EDUCATION, "Education"),
        (OTHER, "Other"),
    )

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default=OTHER)
    owner = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="businesses",
    )
    community = models.ForeignKey(
        "communities.Community",
        on_delete=models.SET_NULL,
        null=True,
        related_name="businesses",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    rejection_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class BusinessBranch(models.Model):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
    )

    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="branches"
    )
    community = models.ForeignKey(
        "communities.Community",
        on_delete=models.SET_NULL,
        null=True,
        related_name="branches",
    )
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=25)
    contact_email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    rejection_reason = models.TextField(null=True, blank=True)
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


class BusinessRating(models.Model):
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="ratings"
    )
    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="business_ratings"
    )
    stars = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="1-10, representing 0.5 to 5.0 stars in half-star steps.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("business", "user")

    def __str__(self):
        return f"{self.user} rated {self.business.name} - {self.stars / 2} stars"


class Follow(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "business"], name="unique_follower_business"
            )
        ]

    def __str__(self):
        return f"{self.follower} followed {self.business.name}"
