from django.db import models


# Create your models here.
class Community(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admins = models.ManyToManyField(
        "accounts.User",
        blank=True,
        related_name="administered_communities",
        limit_choices_to={"role": "community admin"},
    )
    applications_open = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CommunityAdminApplication(models.Model):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
    )

    applicant = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="admin_applications",
    )
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name="admin_applications"
    )
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default=PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_applications",
    )

    def __str__(self):
        return f"{self.applicant.email} - {self.community.name} - {self.status}"
