from rest_framework import serializers

from .models import Comment, Like, Post, PostMedia, Report


class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ["id", "file", "media_type", "file_size", "duration", "created_at"]
        read_only_fields = ["created_at"]


class PostSerializer(serializers.ModelSerializer):
    media = PostMediaSerializer(many=True, read_only=True)
    like_count = serializers.IntegerField(source="likes.count", read_only=True)
    comment_count = serializers.IntegerField(source="comments.count", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "branch",
            "community",
            "post_type",
            "content",
            "status",
            "takedown_reason",
            "media",
            "like_count",
            "comment_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "author",
            "status",
            "takedown_reason",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        request = self.context.get("request")
        media_files = request.FILES.getlist("media") if request else []
        if len(media_files) > 4:
            raise serializers.ValidationError("A post can have at most 4 media items.")
        if not data.get("content") and not media_files:
            raise serializers.ValidationError(
                "A post must have content or at least one media item."
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "author", "post", "content", "is_active", "created_at"]
        read_only_fields = ["author", "is_active", "created_at"]


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "user", "post", "created_at"]
        read_only_fields = ["user", "created_at"]


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            "id",
            "reporter",
            "post",
            "comment",
            "reason",
            "is_reviewed",
            "reviewed_at",
            "created_at",
        ]
        read_only_fields = ["reporter", "is_reviewed", "reviewed_at", "created_at"]

    def validate(self, data):
        post = data.get("post")
        comment = data.get("comment")
        if not post and not comment:
            raise serializers.ValidationError(
                "A report must target either a post or a comment."
            )
        if post and comment:
            raise serializers.ValidationError(
                "A report cannot target both a post and a comment."
            )
        return data
