from django.db import models


# Create your models here.
class Notification(models.Model):
    LIKE = "like"
    COMMENT = "comment"
    BUSINESS_APPROVAL = "business_approval"
    ANNOUNCEMENT = "announcement"
    REPORT_OUTCOME = "report_outcome"
    NEW_FOLLOWER = "new_follower"

    NOTIFICATION_TYPE_CHOICES = (
        (LIKE, "Like"),
        (COMMENT, "Comment"),
        (BUSINESS_APPROVAL, "Business Approval"),
        (ANNOUNCEMENT, "Announcement"),
        (REPORT_OUTCOME, "Report Outcome"),
        (NEW_FOLLOWER, "New Follower"),
    )
    recipient = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="notifications"
    )
    actor = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    notification_type = models.CharField(
        max_length=30, choices=NOTIFICATION_TYPE_CHOICES
    )
    message = models.CharField(max_length=255)
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    comment = models.ForeignKey(
        "posts.Comment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    announcement = models.ForeignKey(
        "announcements.Announcement",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    actor_count = models.PositiveIntegerField(default=1)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.notification_type} -> {self.recipient}"
