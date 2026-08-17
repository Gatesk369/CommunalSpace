from django.db import models


# Create your models here.
class Announcement(models.Model):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    URGENCY_CHOICES = (
        (INFO, "Info"),
        (WARNING, "Warning"),
        (CRITICAL, "Critical"),
    )
    title = models.CharField(max_length=255)
    content = models.TextField
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default=INFO)
    communities = models.ManyToManyField(
        "communities.Community", related_name="announcements"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.urgency}] {self.title}"
