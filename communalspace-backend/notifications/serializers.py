from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "message",
            "actor",
            "actor_count",
            "post",
            "comment",
            "business",
            "announcement",
            "is_read",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
