from django.db import models


# Create your models here.
class Post(models.Model):
    USER = "user"
    BUSINESS = "business"
    POST_TYPE_CHOICES = (
        (USER, "User"),
        (BUSINESS, "Business"),
    )

    ACTIVE = "active"
    UNDER_REVIEW = "under_review"
    REMOVED = "removed"
    STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (UNDER_REVIEW, "Under Review"),
        (REMOVED, "Removed"),
    )
    author = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="posts",
    )
    branch = models.ForeignKey(
        "businesses.BusinessBranch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )
    community = models.ForeignKey(
        "communities.Community",
        on_delete=models.SET_NULL,
        null=True,
        related_name="posts",
    )
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default=USER)
    content = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    takedown_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.author} - {self.community} - {self.created_at}"


class PostMedia(models.Model):
    IMAGE = "image"
    VIDEO = "video"
    GIF = "gif"
    MEDIA_TYPE_CHOICES = (
        (IMAGE, "Image"),
        (VIDEO, "Video"),
        (GIF, "GIF"),
    )

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to="posts/media/")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    file_size = models.IntegerField()
    duration = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post} - {self.media_type}"


class Like(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="likes",
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                name="unique_user_post_like",
            )
        ]

    def __str__(self):
        return f"{self.user} liked {self.post}"


class Comment(models.Model):
    author = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="comments",
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    content = models.TextField()
    takedown_reason = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} on {self.post}"


class CommentLike(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="comment_likes",
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "comment"],
                name="unique_user_comment_like",
            )
        ]


class Report(models.Model):
    SPAM = "spam"
    ABUSE = "abuse"
    MISINFO = "misinfo"
    OTHER = "other"
    REASON_CHOICES = (
        (SPAM, "Spam"),
        (ABUSE, "Abuse"),
        (MISINFO, "Misinformation"),
        (OTHER, "Other"),
    )

    reporter = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="reports",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports",
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports",
    )
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    is_reviewed = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = f"post {self.post_id}" if self.post else f"comment {self.comment_id}"
        return f"{self.reporter} reported {target} for {self.reason}"
